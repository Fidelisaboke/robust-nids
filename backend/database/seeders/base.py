class BaseSeeder:
    """Base class for all seeders"""

    @classmethod
    def run(cls):
        """Run the seeder - to be implemented by subclasses"""
        raise NotImplementedError('Seeder must implement run() method')

    @classmethod
    def log_seeding(cls, model_name, records_count):
        print(f'✅ Seeded {records_count} {model_name} records')
