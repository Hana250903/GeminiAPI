# --- Hàm tiện ích chung để deserialize dictionary thành dataclass (GIỮ NGUYÊN) ---
from dataclasses import field

def deserialize_to_dataclass(cls, data_dict):
    """
    Recursively deserializes a dictionary into a dataclass instance,
    handling nested dataclasses and lists of dataclasses.
    """
    if not isinstance(data_dict, dict):
        raise TypeError(f"Expected dictionary for dataclass {cls.__name__}, got {type(data_dict)}")

    dataclass_fields = {f.name: f for f in cls.__dataclass_fields__.values()}
    
    init_args = {}
    for field_name, field_def in dataclass_fields.items():
        if field_name not in data_dict:
            if field_def.default is field:
                if field_def.default_factory is None:
                    if hasattr(field_def.type, '__origin__') and field_def.type.__origin__ is type(None):
                        init_args[field_name] = None
                    else:
                        raise KeyError(f"Missing required field: '{field_name}' for dataclass {cls.__name__}")
                else:
                    init_args[field_name] = field_def.default_factory()
            else:
                init_args[field_name] = field_def.default
            continue

        value = data_dict[field_name]
        field_type = field_def.type

        if hasattr(field_type, '__origin__') and field_type.__origin__ is type(None):
            if value is None:
                init_args[field_name] = None
                continue
            actual_type = [arg for arg in field_type.__args__ if arg is not type(None)][0]
        else:
            actual_type = field_type

        if hasattr(actual_type, '__origin__') and actual_type.__origin__ is list:
            item_type = actual_type.__args__[0]
            if hasattr(item_type, '__dataclass_fields__'):
                init_args[field_name] = [deserialize_to_dataclass(item_type, item_data) for item_data in value]
            else:
                init_args[field_name] = value
        elif hasattr(actual_type, '__dataclass_fields__'):
            init_args[field_name] = deserialize_to_dataclass(actual_type, value)
        else:
            init_args[field_name] = value

    return cls(**init_args)