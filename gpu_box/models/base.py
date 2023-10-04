class ModelRouteRegistry:
    _registry = {}  # Store model classes by their names

    def __init__(self):
        self.instances = {}

    @classmethod
    def register_model(cls, model_class):
        """Register a model class."""
        model_name = model_class.name
        if model_name in cls._registry:
            raise ValueError(f"ModelRoute '{model_name}' already registered!")
        cls._registry[model_name] = model_class

    @classmethod
    def get_model(cls, model_name):
        """Retrieve a model class by its name."""
        return cls._registry[model_name]

    @classmethod
    def get_models(cls):
        return cls._registry

    @classmethod
    def create_model_instance(cls, model_name, *args, **kwargs):
        """Create an instance of a model by its name."""
        model_class = cls.get_model(model_name)
        return model_class(*args, **kwargs)

    def create_model_instances(self):
        """Create an instance of a model by its name."""
        for model_name, model_cls in self._registry.items():
            self.instances[model_name] = model_cls()
        return self.instances

    def load_model(self, model_name):
        model_instance = self.instances[model_name]
        if model_instance.enabled:
            return
        model_instance.load()

    def unload_model(self, model_name):
        model_instance = self.instances[model_name]
        if not model_instance.enabled:
            return
        model_instance.unload()


class NotLoadedError(Exception):
    pass


class ModelRoute:
    """A base model to be subclassed.
    The role of this model is to rapidly enable adding models by just setting a name, and a typed run function.
    The run function's signature is then inspected in order to prep the input and output shapes (to/from bytes, json, etc).
    """

    name = "override_me"
    model = None

    async def run(self, input_data):
        raise NotImplementedError("run() must be overridden!")

    async def load_and_run(self, input_data):
        if not self.loaded:
            self.model = self.load()
        print(self)
        return await self.run(input_data)

    @property
    def enabled(self):
        return self.model is not None

    @property
    def loaded(self):
        return self.model is not None

    def load(self):
        raise NotImplementedError("load() must be overridden!")

    def unload(self):
        self.model = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ModelRouteRegistry.register_model(cls)

    def __init__(self, lazy=True):
        if not lazy:
            self.model = self.load()

    def __repr__(self):
        load_str = " (loaded)" if self.loaded else ""
        return f"{self.__class__.__name__}({self.name}){load_str}: {self.__doc__}"
