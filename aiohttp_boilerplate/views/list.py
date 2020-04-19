import warnings

from .retrieve import RetrieveView


class ListView(RetrieveView):
    default_limit = "50"

    def __init__(self, request):
        super().__init__(request)
        self.objects = self.get_objects()
        self.limit = self.get_limit()
        self.order = self.get_order()
        self.offset = self.get_offset()
        self.count = None

    # Return model object
    def get_model(self):
        warnings.warn('Redefine get_schema in inherited class', RuntimeWarning)
        return None

    # Return objects list
    def get_objects(self):
        return self.get_model()(is_list=True)

    @staticmethod
    def str_to_int(value: str):
        try:
            value = int(value)
        except (ValueError, TypeError):
            value = None
        return value

    # Return limit for sql query
    def get_limit(self):
        # TODO
        # Create consts for default limit amount
        return self.str_to_int(self.request.query.get('limit', self.default_limit))

    # Return offset for sql query
    def get_offset(self):
        return self.str_to_int(self.request.query.get("offset"))

    # Return order
    def get_order(self):
        return ''

    def join_beautiful_output(self, aliases, data):

        beautiful_data = []
        for row in data:
            temp = super().join_beautiful_output(aliases, row)
            beautiful_data.append(temp)

        return beautiful_data

    async def perform_get(self, fields="", where="", order="", limit=50, offset=None, params=None):
        aliases, fields = self.join_prepare_fields(fields)
        raw_data = await self.objects.sql.select(
            fields=fields,
            where=where,
            order=order,
            limit=limit,
            offset=offset,
            params=params,
            many=True,
        )
        self.objects.set_data(self.join_beautiful_output(aliases, raw_data))

    async def perform_get_count(self, where, params):
        return await self.objects.sql.get_count(where=where, params=params)

    async def get_count(self, where='', params=None):
        params = params or {}
        if self.count is None:
            self.count = await self.perform_get_count(where, params)
        return self.count

    async def get_data(self, objects):
        data = []
        for obj in objects:
            data.append(await super().get_data(obj))

        return data

    async def _get(self):
        await self.on_start()

        await self.before_get()
        await self.perform_get(
            fields=self.fields,
            where=self.where,
            limit=self.limit,
            offset=self.offset,
            order=self.order,
            params=self.params,
        )
        await self.after_get()

        return {
            'data': await self.get_data(self.objects.data),
            'count': await self.get_count(
                where=self.where,
                params=self.params,
            )
        }

    async def get(self):
        return self.json_response(await self._get())
