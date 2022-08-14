# Generated by Django 3.2.14 on 2022-08-04 06:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bank',
         '0014_auto_20220804_trigger_check_account_balance_with_transactions_insert_update_delete'),
    ]

    operations = [
        migrations.RunSQL('''
            -- FUNCTION: public.check_all_transactions_value_summation_must_be_zero()

            -- DROP FUNCTION IF EXISTS public.check_all_transactions_value_summation_must_be_zero();

            CREATE OR REPLACE FUNCTION public.check_all_transactions_value_summation_must_be_zero()
                RETURNS trigger
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE NOT LEAKPROOF
            AS $BODY$
            declare
                all_transactions_value integer;
            begin
                all_transactions_value := (
                    select sum(value) from bank_accounttransaction
                );
                if all_transactions_value <> 0 then
                    raise exception 'transactions summation must be zero.';
                end if;
                return new;
            end;
            $BODY$;

            ALTER FUNCTION public.check_all_transactions_value_summation_must_be_zero()
                OWNER TO nakhll;
        ''', reverse_sql='DROP FUNCTION IF EXISTS public.check_all_transactions_value_summation_must_be_zero();'),
        migrations.RunSQL('''
            -- Trigger: check_all_transactions_value_summation_must_be_zero_post_insert

            -- DROP TRIGGER IF EXISTS check_all_transactions_value_summation_must_be_zero_post_insert ON public.bank_accounttransaction;

            CREATE CONSTRAINT TRIGGER check_all_transactions_value_summation_must_be_zero_post_insert
                AFTER INSERT OR DELETE OR UPDATE
                ON public.bank_accounttransaction
                DEFERRABLE INITIALLY DEFERRED
                FOR EACH ROW
                EXECUTE FUNCTION public.check_all_transactions_value_summation_must_be_zero();
        ''', reverse_sql='DROP TRIGGER IF EXISTS check_all_transactions_value_summation_must_be_zero_post_insert ON public.bank_accounttransaction;')
    ]