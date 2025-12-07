from textual.validation import Function, Number, ValidationResult, Validator
from tdtui.textual_assets import textual_instance_config


class ValidExtPort(Validator):
    def __init__(self, app, instance, failure_description: str | None = None):
        super().__init__(failure_description=failure_description)
        self.app = app
        self.instance = instance

    def validate(self, value: int) -> ValidationResult:
        if textual_instance_config.validate_port(value) == False:
            return self.failure(
                f"{value} is not a valid port number. Please enter 1–65535."
            )

        in_use_by = textual_instance_config.port_in_use(
            app=self.app, port=value, current_instance_name=self.instance.name
        )

        if in_use_by is not None:
            return self.failure(
                f"Port {value} is already in use by instance '{in_use_by}'. "
                "Please choose a different port."
            )
        else:
            return self.success()


class ValidIntPort(ValidExtPort):
    def validate(self, value: int) -> ValidationResult:
        if value == self.instance.arg_ext:
            return self.failure(
                "Internal port must not be the same as external port. "
                "Please choose another port."
            )
        super().validate(value)
