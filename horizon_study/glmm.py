"""
glmm.py — crossed random-intercept GLMM / LMM by sparse penalised IRLS + Laplace.

Model:  g(E[y]) = X beta + sum_k Z_k u_k,   u_k ~ N(0, sigma_k^2 I)
Random-effect blocks are arbitrary factors (event, model, model-by-horizon slope),
crossed, encoded as sparse one-hot (or one-hot times a covariate) matrices.

Estimation (the lme4 nAGQ=1 recipe): for a candidate set of log-variances the
inner loop solves the Henderson augmented normal equations for (beta, u) by
IRLS; the outer loop maximises the Laplace-approximate marginal log-likelihood
over the variances (Nelder–Mead). Fixed-effect SEs come from the beta block of
the inverse augmented Hessian at the optimum. For the Gaussian family the
Laplace approximation is exact (ML).
"""
from __future__ import annotations
import numpy as np, scipy.sparse as sp
from scipy.sparse.linalg import splu
from scipy.optimize import minimize


def onehot(levels, weight=None):
    codes, uniq = np.unique(levels, return_inverse=True)[1], np.unique(levels)
    data = np.ones(len(codes)) if weight is None else np.asarray(weight, float)
    return sp.csc_matrix((data, (np.arange(len(codes)), codes)), shape=(len(codes), len(uniq))), uniq


class CrossedGLMM:
    def __init__(self, family="binomial"):
        assert family in ("binomial", "gaussian"); self.family = family

    def _pirls(self, theta, beta0=None, u0=None, maxit=40, tol=1e-8):
        X, Zs, y = self.X, self.Zs, self.y
        n, p = X.shape; q = sum(Z.shape[1] for Z in Zs); Z = sp.hstack(Zs, format="csc")
        sig2 = np.exp(theta[:len(Zs)]); s2 = np.exp(theta[len(Zs)]) if self.family == "gaussian" else 1.0
        dinv = np.concatenate([np.full(Z_.shape[1], 1 / s) for Z_, s in zip(Zs, sig2)])
        beta = np.zeros(p) if beta0 is None else beta0.copy(); u = np.zeros(q) if u0 is None else u0.copy()
        XZ = sp.hstack([sp.csc_matrix(X), Z], format="csc")
        for it in range(maxit):
            eta = X @ beta + Z @ u
            if self.family == "binomial":
                mu = 1 / (1 + np.exp(-eta)); w = mu * (1 - mu) + 1e-10; z = eta + (y - mu) / w
            else:
                mu = eta; w = np.full(n, 1 / s2); z = y
            Wd = sp.diags(w)
            H = (XZ.T @ Wd @ XZ).tocsc() + sp.diags(np.concatenate([np.zeros(p), dinv]))
            rhs = XZ.T @ (w * z)
            lu = splu(H.tocsc()); sol = lu.solve(rhs)
            beta_new, u_new = sol[:p], sol[p:]
            done = np.max(np.abs(np.concatenate([beta_new - beta, u_new - u]))) < tol
            beta, u = beta_new, u_new
            if done or self.family == "gaussian":
                break
        eta = X @ beta + Z @ u
        if self.family == "binomial":
            mu = 1 / (1 + np.exp(-eta)); ll = np.sum(y * np.log(mu + 1e-12) + (1 - y) * np.log(1 - mu + 1e-12))
            w = mu * (1 - mu) + 1e-10
        else:
            r = y - eta; ll = -0.5 * (np.sum(r * r) / s2 + n * np.log(2 * np.pi * s2)); w = np.full(n, 1 / s2)
        # Laplace: ll - 0.5 u' D^-1 u - 0.5 log|D| - 0.5 log|Z'WZ + D^-1|
        Huu = (Z.T @ sp.diags(w) @ Z).tocsc() + sp.diags(dinv)
        lu_uu = splu(Huu)
        logdet = np.sum(np.log(np.abs(lu_uu.U.diagonal())))
        logD = sum(Z_.shape[1] * np.log(s) for Z_, s in zip(Zs, sig2))
        lap = ll - 0.5 * np.sum(u * u * dinv) - 0.5 * logD - 0.5 * logdet
        return lap, beta, u, lu, H, w

    def fit(self, y, X, Zs, names_fixed, names_vc, maxfun=400):
        self.y = np.asarray(y, float); self.X = np.asarray(X, float); self.Zs = [Z.tocsc() for Z in Zs]
        k = len(Zs) + (1 if self.family == "gaussian" else 0)
        theta0 = np.zeros(k); state = {"beta": None, "u": None}
        def obj(theta):
            theta = np.clip(theta, -12, 8)
            lap, b, u, *_ = self._pirls(theta, state["beta"], state["u"]); state["beta"], state["u"] = b, u
            return -lap
        res = minimize(obj, theta0, method="Nelder-Mead", options=dict(maxfev=maxfun, xatol=1e-3, fatol=1e-3))
        theta = np.clip(res.x, -12, 8)
        lap, beta, u, lu, H, w = self._pirls(theta, state["beta"], state["u"])
        p = self.X.shape[1]
        # beta covariance = top-left block of H^-1
        Hinv_cols = np.column_stack([lu.solve(e) for e in np.eye(H.shape[0])[:, :p].T])
        cov_b = Hinv_cols[:p, :]
        se = np.sqrt(np.maximum(np.diag(cov_b), 0))
        out = dict(converged=bool(res.success), laplace_loglik=float(lap), n=len(self.y), n_fixed=p,
                   coef={nm: dict(mean=float(b), sd=float(s), ci_lo=float(b - 1.96 * s), ci_hi=float(b + 1.96 * s), z=float(b / s) if s > 0 else float("nan"))
                         for nm, b, s in zip(names_fixed, beta, se)},
                   vc_sd={nm: float(np.sqrt(np.exp(t))) for nm, t in zip(names_vc, theta[:len(Zs)])})
        if self.family == "gaussian":
            out["resid_sd"] = float(np.sqrt(np.exp(theta[len(Zs)])))
        out["random_effects"] = {}
        off = 0
        for nm, Z_ in zip(names_vc, self.Zs):
            out["random_effects"][nm] = u[off:off + Z_.shape[1]]; off += Z_.shape[1]
        return out


def fit_crossed(df, y_col, fixed_cols, family="binomial", random_slope_col=None, event_col="id", model_col="model"):
    """Convenience: intercept + fixed_cols, random intercepts for event and model (+ optional random slope by model)."""
    X = np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in fixed_cols])
    Ze, _ = onehot(df[event_col].to_numpy()); Zm, mlev = onehot(df[model_col].to_numpy())
    Zs, names = [Ze, Zm], ["event", "model"]
    if random_slope_col:
        Zs_, _ = onehot(df[model_col].to_numpy(), weight=df[random_slope_col].to_numpy(float)); Zs.append(Zs_); names.append(f"model:{random_slope_col}")
    r = CrossedGLMM(family).fit(df[y_col].to_numpy(float), X, Zs, ["intercept"] + list(fixed_cols), names)
    r["model_levels"] = list(mlev); r["method"] = f"crossed random intercepts (event, model{', model slope' if random_slope_col else ''}), Laplace/PIRLS, {family}"
    r["random_effects"] = {k: v.tolist() if k != "event" else None for k, v in r["random_effects"].items()}
    return r
