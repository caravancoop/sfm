from reversion import register


def versionable(*method_names):
    def save_overrider(cls):

        @register
        class VersionableClass(cls):
            def save(self):
                print("VERSION HOOK YO")
                return super(cls, self).save()

        return VersionableClass
    return save_overrider
