import importlib

def class_for_name(class_name, module_name="person.models"):
    module = importlib.import_module(module_name)
    class_ = getattr(module, class_name)
    return class_
