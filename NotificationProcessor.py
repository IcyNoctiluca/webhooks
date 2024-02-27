# Define the interface for the strategy
class Strategy:
    def execute(self, webhook: dict):
        pass


# Concrete implementations of the strategy
class AuthorisationStrategy(Strategy):
    def execute(self, webhook: dict):
        # store authed payment in DB
        print("Executing AuthorisationStrategy")


class RecurringContractStrategy(Strategy):
    def execute(self, webhook: dict):
        # store recurring contract in DB
        print("Executing RecurringContractStrategy")


class ReportAvailableStrategy(Strategy):
    def execute(self, webhook: dict):
        # get report through SFTP
        print("Executing ReportAvailableStrategy")


# Example usage
if __name__ == "__main__":
    # Create instances of strategies
    strategy_a = STRATEGY_MAP["AUTHORIZATION"]

    strategy_a.execute()
