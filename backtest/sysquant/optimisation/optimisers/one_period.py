from backtest.sysquant.optimisation.weights import estimatesWithPortfolioWeights
from backtest.sysquant.estimators.estimates import Estimates
from backtest.sysquant.optimisation.shared import optimise_given_estimates


def one_period_optimisation(
    estimates: Estimates, **weighting_kwargs
) -> estimatesWithPortfolioWeights:

    estimates_with_portfolio_weights = optimise_given_estimates(
        estimates=estimates, **weighting_kwargs
    )

    return estimates_with_portfolio_weights
