from .permissions import PermissionSeeder
from .role_permissions import RolePermissionSeeder
from .roles import RoleSeeder
from .users import UserSeeder


class SeederManager:
    """Manage the seeding process"""

    @staticmethod
    def run_all():
        """Run all seeders in proper order"""
        print('🌱 Starting database seeding...')

        seeders = [PermissionSeeder, RoleSeeder, RolePermissionSeeder, UserSeeder]

        for seeder in seeders:
            try:
                seeder.run()
            except Exception as e:
                print(f'❌ Error running {seeder.__name__}: {e}')
                raise

        print('🎉 Database seeding completed successfully!')
