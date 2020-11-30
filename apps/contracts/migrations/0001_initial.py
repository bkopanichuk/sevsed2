# Generated by Django 3.1 on 2020-11-14 06:06

import apps.contracts.models.contract_model
import apps.contracts.models.dict_model
import apps.l_core.mixins
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.crypto
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccrualProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('count', models.IntegerField(default=1)),
                ('price', models.FloatField(default=0)),
                ('total_price', models.FloatField(default=0)),
                ('pdv', models.FloatField(default=0)),
                ('total_price_pdv', models.FloatField(default=0)),
            ],
            options={
                'verbose_name': 'Послуги(товари) по договору',
                'verbose_name_plural': 'Послуги(товари) по договору',
            },
            bases=(apps.contracts.models.contract_model.ProductMixin, apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='AccrualSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('charging_day', models.IntegerField(verbose_name='Дата місяця на яку необхідно здійснювати нарахування оплати')),
                ('start_period', models.DateField(verbose_name='Початок дії тарифного плану')),
                ('end_period', models.DateField(default=apps.contracts.models.contract_model.default_end_period, verbose_name='Кінець дії тарифного плану')),
                ('is_legal', models.BooleanField(default=True, editable=False, verbose_name='Вказує чи тарифний план наразі дійсний')),
                ('count', models.IntegerField(default=1)),
                ('price', models.FloatField(default=0)),
                ('total_price', models.FloatField(default=0)),
                ('pdv', models.FloatField(default=0)),
                ('total_price_pdv', models.FloatField(default=0)),
            ],
            options={
                'verbose_name': 'Послуги(товари) по договору',
                'verbose_name_plural': 'Послуги(товари) по договору',
            },
            bases=(apps.contracts.models.contract_model.ProductMixin, apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('number_contract', models.TextField(max_length=50, null=True, verbose_name='№ Договору')),
                ('subject_contract', models.TextField(max_length=500, null=True, verbose_name='Предмет договору')),
                ('price_contract', models.FloatField(default=0, verbose_name='Ціна договору')),
                ('price_contract_by_month', models.FloatField(default=0, verbose_name='Ціна договору за місяць')),
                ('price_additional_services', models.FloatField(default=0, verbose_name='Вартість додаткових послуг(підключення і тд)')),
                ('contract_time', models.IntegerField(blank=True, null=True, verbose_name='Строк дії договору')),
                ('one_time_service', models.BooleanField(default=False, verbose_name='Одноразова послуга/купівля')),
                ('start_date', models.DateField(verbose_name='Дата заключення договору')),
                ('start_of_contract', models.DateField(verbose_name='Дата початку дії договору')),
                ('start_accrual', models.DateField(null=True, verbose_name='Дата початку нарахувань')),
                ('expiration_date', models.DateField(verbose_name='Дата закінчення')),
                ('copy_contract', models.FileField(null=True, upload_to='uploads/copy_contract/%Y/%m/%d/', verbose_name='Копія договору')),
                ('contract_docx', models.FileField(null=True, upload_to='uploads/contract_docx/%Y/%m/%d/', verbose_name='Проект договору')),
                ('status', models.CharField(choices=[['future', 'Укладається'], ['actual', 'Дійсний'], ['archive', 'Архівний'], ['rejected', 'Не заключений']], default='future', max_length=20, verbose_name='Статус')),
                ('change_status_reason', models.CharField(max_length=200, null=True, verbose_name='Причина зміни статусу')),
                ('automatic_number_gen', models.BooleanField(default=False, verbose_name='Сформувати номер автоматично?')),
            ],
            options={
                'verbose_name': 'Договір',
                'verbose_name_plural': 'Договори',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='ContractFinance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('last_date_accrual', models.DateField(null=True, verbose_name='Дата останніх нарахувань')),
                ('total_size_accrual', models.FloatField(default=0, verbose_name='Розмір нарахувань (Загальний)')),
                ('last_date_pay', models.DateField(null=True, verbose_name='Дата останніх нарахувань')),
                ('total_size_pay', models.FloatField(default=0, verbose_name='Розмір нарахувань (Загальний)')),
                ('total_balance', models.FloatField(default=0, verbose_name='Баланс')),
            ],
            options={
                'verbose_name': 'Баланс по договору',
                'verbose_name_plural': 'Баланс по договорах',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='ContractProducts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('count', models.IntegerField(default=1)),
                ('price', models.FloatField(default=0)),
                ('total_price', models.FloatField(default=0)),
                ('pdv', models.FloatField(default=0)),
                ('total_price_pdv', models.FloatField(default=0)),
            ],
            options={
                'verbose_name': 'Послуги(товари) по договору',
                'verbose_name_plural': 'Послуги(товари) по договору',
            },
            bases=(apps.contracts.models.contract_model.ProductMixin, apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='ContractSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('charging_day', models.IntegerField(verbose_name='Дата місяця на яку необхідно здійснювати нарахування оплати')),
                ('start_period', models.DateField(verbose_name='Початок дії тарифного плану')),
                ('end_period', models.DateField(default=apps.contracts.models.contract_model.default_end_period, verbose_name='Кінець дії тарифного плану')),
                ('is_legal', models.BooleanField(default=True, editable=False, verbose_name='Вказує чи тарифний план наразі дійсний')),
                ('count', models.IntegerField(default=1)),
                ('price', models.FloatField(default=0)),
                ('total_price', models.FloatField(default=0)),
                ('pdv', models.FloatField(default=0)),
                ('total_price_pdv', models.FloatField(default=0)),
            ],
            options={
                'verbose_name': 'Послуги(товари) по договору',
                'verbose_name_plural': 'Послуги(товари) по договору',
            },
            bases=(apps.contracts.models.contract_model.ProductMixin, apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='Coordination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('subject', models.TextField(verbose_name='Особа')),
                ('status', models.BooleanField(default=False, verbose_name='Статус погодження (Так/Ні)')),
                ('start', models.DateField(verbose_name='Початок погодження')),
                ('end', models.DateField(verbose_name='Кінець погодження')),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Погодження договору',
                'verbose_name_plural': 'Погодження договорів',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalContract',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(blank=True, editable=False, null=True)),
                ('date_edit', models.DateTimeField(blank=True, editable=False, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('number_contract', models.TextField(max_length=50, null=True, verbose_name='№ Договору')),
                ('subject_contract', models.TextField(max_length=500, null=True, verbose_name='Предмет договору')),
                ('price_contract', models.FloatField(default=0, verbose_name='Ціна договору')),
                ('price_contract_by_month', models.FloatField(default=0, verbose_name='Ціна договору за місяць')),
                ('price_additional_services', models.FloatField(default=0, verbose_name='Вартість додаткових послуг(підключення і тд)')),
                ('contract_time', models.IntegerField(blank=True, null=True, verbose_name='Строк дії договору')),
                ('one_time_service', models.BooleanField(default=False, verbose_name='Одноразова послуга/купівля')),
                ('start_date', models.DateField(verbose_name='Дата заключення договору')),
                ('start_of_contract', models.DateField(verbose_name='Дата початку дії договору')),
                ('start_accrual', models.DateField(null=True, verbose_name='Дата початку нарахувань')),
                ('expiration_date', models.DateField(verbose_name='Дата закінчення')),
                ('copy_contract', models.TextField(max_length=100, null=True, verbose_name='Копія договору')),
                ('contract_docx', models.TextField(max_length=100, null=True, verbose_name='Проект договору')),
                ('status', models.CharField(choices=[['future', 'Укладається'], ['actual', 'Дійсний'], ['archive', 'Архівний'], ['rejected', 'Не заключений']], default='future', max_length=20, verbose_name='Статус')),
                ('change_status_reason', models.CharField(max_length=200, null=True, verbose_name='Причина зміни статусу')),
                ('automatic_number_gen', models.BooleanField(default=False, verbose_name='Сформувати номер автоматично?')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical Договір',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalStageProperty',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(blank=True, editable=False, null=True)),
                ('date_edit', models.DateTimeField(blank=True, editable=False, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('name', models.TextField(blank=True, default='', null=True, verbose_name='Назва організації')),
                ('address', models.TextField(blank=True, default='', null=True)),
                ('settlement_account', models.CharField(blank=True, max_length=30, null=True, verbose_name='Розрахунковий рахунок')),
                ('bank_name', models.CharField(max_length=200, null=True, verbose_name='Назва банку')),
                ('main_unit', models.CharField(blank=True, max_length=200, null=True, verbose_name='Уповноважена особа')),
                ('main_unit_state', models.CharField(blank=True, max_length=200, null=True, verbose_name='Посада уповноваженої особи')),
                ('mfo', models.CharField(blank=True, max_length=50, null=True, verbose_name='МФО')),
                ('ipn', models.CharField(blank=True, max_length=200, null=True, verbose_name='ІПН')),
                ('certificate_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Номер свідотства ПДВ')),
                ('edrpou', models.CharField(blank=True, max_length=10, null=True, verbose_name='ЄДРПОУ')),
                ('phone', models.CharField(blank=True, max_length=150, null=True, verbose_name='Телефон')),
                ('email', models.CharField(blank=True, max_length=150, null=True, verbose_name='email')),
                ('work_reason', models.TextField(null=True, verbose_name='Працює на підставі')),
                ('statute_copy', models.TextField(max_length=100, null=True, verbose_name='Статутні документи')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical Реквізити договору',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='ImportPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('in_file', models.FileField(upload_to='import_client_bunk/')),
                ('details', django.contrib.postgres.fields.jsonb.JSONField(editable=False, null=True)),
                ('is_imported', models.BooleanField(default=False, editable=False)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view', 'view_self', 'delete_self', 'change_self'),
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='MainActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
            ],
            options={
                'verbose_name': 'Вид основної діяльності',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='OrganizationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
            ],
            options={
                'verbose_name': 'Типів органцізації',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
                ('unit', models.CharField(choices=[['service', 'Послуга'], ['product', 'ТОвар']], max_length=100, verbose_name='Одиничі виміру')),
            ],
            options={
                'verbose_name': 'Послуги,Товари',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model, apps.contracts.models.dict_model.ProductPropertyMixin),
        ),
        migrations.CreateModel(
            name='ProductPriceDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
                ('start_period', models.DateField(verbose_name='Початок дії ціни')),
                ('price', models.FloatField(verbose_name='Ціна')),
                ('pdv', models.FloatField(verbose_name='ПДВ')),
                ('price_pdv', models.FloatField(verbose_name='Ціна з ПДВ')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
            ],
            options={
                'verbose_name': 'Тип власності',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='RegisterAccrual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('title', models.CharField(max_length=150, null=True, verbose_name='Заголовок рахунку')),
                ('accrual_type', models.CharField(choices=[['subscription', 'Абонплата'], ['service', 'Послуги']], max_length=150, null=True, verbose_name='Тип рахунку')),
                ('date_start_period', models.DateField(null=True, verbose_name='Початок періоду')),
                ('date_end_period', models.DateField(null=True, verbose_name='Кінець періоду')),
                ('date_accrual', models.DateField(null=True, verbose_name='Дата нарахувань')),
                ('mb_size', models.FloatField(null=True, verbose_name='Кількість мегабайт (фактично)')),
                ('mb_size_tariff', models.FloatField(null=True, verbose_name='Кількість мегабайт в тарифі')),
                ('mb_size_over_tariff', models.FloatField(null=True, verbose_name='Кількість мегабайт понад тариф')),
                ('size_accrual', models.FloatField(null=True, verbose_name='Розмір нарахувань')),
                ('pay_size', models.FloatField(null=True, verbose_name='Сума до сплати')),
                ('balance', models.FloatField(null=True, verbose_name='Баланс на поточний період')),
                ('penalty', models.FloatField(null=True, verbose_name='Пеня за попередній період')),
                ('accrual_docx', models.FileField(null=True, upload_to='uploads/accrual_docx/%Y/%m/%d/', verbose_name='Проект Рахунку')),
                ('date_sending_doc', models.DateField(null=True, verbose_name='Дата відправлення акту')),
                ('is_doc_send_successful', models.BooleanField(null=True, verbose_name='Акт успішно відправлено?')),
            ],
            options={
                'verbose_name': 'Нарахування',
                'verbose_name_plural': 'Нарахування',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='RegisterAct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('number_act', models.TextField(verbose_name='Номер акту')),
                ('date_formation_act', models.DateField(verbose_name='Дата формування акту')),
                ('date_sending_act', models.DateField(null=True, verbose_name='Дата відправлення акту')),
                ('is_send_successful', models.BooleanField(null=True, verbose_name='Акт успішно відправлено?')),
                ('date_return_act', models.DateField(null=True, verbose_name='Дата повернення акту')),
                ('copy_act', models.FileField(null=True, upload_to='uploads/docx_act/%Y/%m/%d/', verbose_name='Копія акту(DOCX)')),
                ('copy_act_pdf', models.FileField(null=True, upload_to='uploads/pdf_act/%Y/%m/%d/', verbose_name='Копія акту(PDF)')),
                ('sign_act_from_contractor', models.TextField(help_text='Підписант може накласти цифровий підпис на копію акту в пдф', null=True, verbose_name='Цифровий підпис контрагента')),
                ('copy_act_from_contractor', models.FileField(help_text='Повинна містити скановану копію з штампом організації підписанта', null=True, upload_to='uploads/pdf_act_stamp/%Y/%m/%d/', verbose_name='Копія акту підписана контрагентом')),
            ],
            options={
                'verbose_name': 'Акт',
                'verbose_name_plural': 'Акти',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='RegisterPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('payment_date', models.DateField(null=True, verbose_name='Дата оплати')),
                ('outer_doc_number', models.CharField(max_length=100, null=True, verbose_name='Зовнішній номер документа платежу')),
                ('payment_type', models.CharField(choices=[['import', 'Клієнт-банк'], ['handly', 'Вручну']], default='handly', max_length=100)),
                ('sum_payment', models.IntegerField(null=True, verbose_name='Число')),
            ],
            options={
                'verbose_name': 'Платіж',
                'verbose_name_plural': 'Платежі',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Типи послуг',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='StageProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('name', models.TextField(blank=True, default='', null=True, verbose_name='Назва організації')),
                ('address', models.TextField(blank=True, default='', null=True)),
                ('settlement_account', models.CharField(blank=True, max_length=30, null=True, verbose_name='Розрахунковий рахунок')),
                ('bank_name', models.CharField(max_length=200, null=True, verbose_name='Назва банку')),
                ('main_unit', models.CharField(blank=True, max_length=200, null=True, verbose_name='Уповноважена особа')),
                ('main_unit_state', models.CharField(blank=True, max_length=200, null=True, verbose_name='Посада уповноваженої особи')),
                ('mfo', models.CharField(blank=True, max_length=50, null=True, verbose_name='МФО')),
                ('ipn', models.CharField(blank=True, max_length=200, null=True, verbose_name='ІПН')),
                ('certificate_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Номер свідотства ПДВ')),
                ('edrpou', models.CharField(blank=True, max_length=10, null=True, verbose_name='ЄДРПОУ')),
                ('phone', models.CharField(blank=True, max_length=150, null=True, verbose_name='Телефон')),
                ('email', models.CharField(blank=True, max_length=150, null=True, verbose_name='email')),
                ('work_reason', models.TextField(null=True, verbose_name='Працює на підставі')),
                ('statute_copy', models.FileField(null=True, upload_to='', verbose_name='Статутні документи')),
            ],
            options={
                'verbose_name': 'Реквізити договору',
                'verbose_name_plural': 'Реквізити договорів',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
            ],
            options={
                'verbose_name': 'Обслуговування, абонплата',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model, apps.contracts.models.dict_model.ProductPropertyMixin),
        ),
        migrations.CreateModel(
            name='SubscriptionPriceDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
                ('start_period', models.DateField(verbose_name='Початок дії ціни')),
                ('price', models.FloatField(verbose_name='Ціна')),
                ('pdv', models.FloatField(verbose_name='ПДВ')),
                ('price_pdv', models.FloatField(verbose_name='Ціна з ПДВ')),
                ('unit', models.CharField(choices=[['mb', 'Мегабайти']], default='mb', max_length=100, verbose_name='Одиничі виміру')),
                ('s_count', models.FloatField(null=True, verbose_name='Кількість ')),
            ],
            options={
                'abstract': False,
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='TariffChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('start_date', models.DateField(editable=False, verbose_name='Дата початку дії договору')),
            ],
            options={
                'verbose_name': 'Зміна тарифного плану',
                'verbose_name_plural': 'Зміна тарифного плану',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
        migrations.CreateModel(
            name='TemplateDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_uuid', models.UUIDField(default=uuid.uuid4)),
                ('date_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_edit', models.DateTimeField(auto_now=True, null=True)),
                ('is_deleted', models.BooleanField(db_index=True, default=False, editable=False)),
                ('is_group', models.BooleanField(default=False)),
                ('code', models.SlugField(default=django.utils.crypto.get_random_string, verbose_name='Код')),
                ('name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Значення')),
                ('template_file', models.FileField(null=True, upload_to='uploads/doc_templates/%Y/%m/%d/', verbose_name='Шаблон документу (договору)')),
                ('related_model_name', models.SlugField(max_length=100, unique=True, verbose_name='Шаблон документу')),
            ],
            options={
                'verbose_name': 'Шаблон документу',
            },
            bases=(apps.l_core.mixins.CheckProtected, apps.l_core.mixins.RelatedObjects, models.Model),
        ),
    ]
