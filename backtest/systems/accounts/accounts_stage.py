## We don't need to inherit from accountForecast, accountInputs, accountBufferingSystemLevel, accountInstruments
## as we get those via these other objects

from backtest.systems.accounts.account_with_multiplier import accountWithMultiplier
from backtest.systems.accounts.account_subsystem import accountSubsystem
from backtest.systems.accounts.account_trading_rules import accountTradingRules


class Account(accountTradingRules, accountWithMultiplier, accountSubsystem):
    @property
    def name(self):
        return "accounts"
