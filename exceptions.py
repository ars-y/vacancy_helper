class URLValueException(ValueError):
    """Exception for URl is not correct."""
    
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
    def __str__(self) -> str:
        if not self.args:
            return 'initial url isn\'t correct'

        return super().__str__()
