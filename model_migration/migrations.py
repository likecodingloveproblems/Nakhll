from model_migration.scripts import (CartItemMigrationScript, CartMigrationScript,
                    CouponConstraintMigrationScript, CouponMigrationScript,
                    CouponUsageMigrationScript, InvoiceMigrationScript,
                    TransactionMigrationScript, TransactionResultMigraitionScript,
                    InvoiceItemMigrationScript, TransactionReverseMigrationScript,
                    TransactionConfirmationMigrationScript)


class Migration:
    def __init__(self, *, scripts='__all__'):
        self._scripts = scripts

    def run(self):
        ''' Get all scripts from .get_migration_scripts() and run them'''
        for script in self.get_migration_script():
            print(f'Migrating {script.__name__} ...')
            script().migrate()
        print('\n  Migration finished successfully')

    def get_migration_script(self):
        if self._scripts == '__all__':
            return [
                CouponMigrationScript,
                CouponConstraintMigrationScript,
                CartMigrationScript,
                CartItemMigrationScript,
                InvoiceMigrationScript,
                InvoiceItemMigrationScript,
                CouponUsageMigrationScript,
                TransactionMigrationScript,
                TransactionResultMigraitionScript,
                TransactionConfirmationMigrationScript,
                TransactionReverseMigrationScript,
            ]
        return self._scripts