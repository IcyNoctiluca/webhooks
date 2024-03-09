import os


def getIsLocalEnvironment() -> bool:
    return not (getIsGoogleAppEnvironment())


def getIsGoogleAppEnvironment() -> bool:
    return os.getenv('GAE_ENV', '').startswith('standard')


# Example usage
if __name__ == "__main__":
    print(getIsLocalEnvironment())
