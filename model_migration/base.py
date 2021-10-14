import datetime, jdatetime
from model_migration.exceptions import SkipItemException



class BaseMigrationScript:
    old_model = None
    new_model = None
    many2many_relation_fields = []
    _datetime_str_format = '%Y-%m-%d %H:%M:%S'
    _date_str_format = '%Y-%m-%d'

    def __init__(self, *, output_file=None):
        self._all_parsed_data = []
        self.output_file = output_file
        

    def migrate(self):
        ''' Get all data from old model, parse them and create new model'''
        old_data = self.get_old_model_data()
        for data in old_data:
            try:
                parsed_data = self.parse_data(data)
                self._all_parsed_data.append(parsed_data)
            except SkipItemException as ex:
                print('Skiping item: {}\t {}'.format(data, ex))
                if self.output_file:
                    self.writelines('Skiping item: {}\t {}\n'.format(data, ex))

        self.create_new_model()

    def __jsonify(self, data):
        ''' Convert data to json '''
        data = data.__dict__
        del data['_state']
        for item in data:
            if isinstance(data[item], datetime.datetime) or isinstance(data[item], jdatetime.datetime):
                data[item] = data[item].strftime(self._datetime_str_format)
            elif isinstance(data[item], datetime.date) or isinstance(data[item], jdatetime.date):
                data[item] = data[item].strftime(self._date_str_format)
        return data

    def get_old_model_data(self):
        ''' Get all data from old model '''
        assert self.old_model is not None, 'old_model is not defined. You should define old_model attribute or override .get_old_model_data()'
        return self.old_model.objects.all()


    def parse_data(self, data):
        ''' Parse old data to new model fields'''
        raise NotImplementedError('`parse_data()` must be implemented.')

    def create_new_model(self):
        ''' Create new model '''
        assert self.new_model is not None, 'new_model is not defined. You should define new_model attribute or override .create_new_model()'
        assert self._all_parsed_data is not [], 'Parsed data is empty. You should parse data before creating new model'
        if self.many2many_relation_fields:
            self.__onebyone_create_method()
        else:
            self.__bulk_create_method()


    def __bulk_create_method(self):
        bulk_list = []
        for data in self._all_parsed_data:
            bulk_list.append(self.new_model(**data))
        self.new_model.objects.bulk_create(bulk_list)

    def __onebyone_create_method(self):
        for data in self._all_parsed_data:
            many2many_fields = dict()
            for item in self.many2many_relation_fields:
                many2many_fields[item] = data.pop(item)
            instance = self.new_model.objects.create(**data)
            for key, value in many2many_fields.items():
                instance_field = getattr(instance, key)
                instance_field.set(value)
            instance.save()

