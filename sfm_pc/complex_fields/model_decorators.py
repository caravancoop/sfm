from reversion import register


def translatable(orig_cls):
    orig_save = orig_cls.save
    def save(self, *args, **kwargs):
        print("Apply magic translation sauce")
        orig_save()


def versioned(orig_cls):
    register(orig_cls)
    return orig_cls
