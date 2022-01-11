# Generated by Django 4.0.1 on 2022-01-11 03:44

import alexandria.searchablefields.mixins
import alexandria.users.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import localflavor.us.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('records', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='USLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_1', models.CharField(max_length=128, verbose_name='Address')),
                ('address_2', models.CharField(blank=True, max_length=128, verbose_name="Address cont'd")),
                ('city', models.CharField(blank=True, max_length=64, null=True, verbose_name='City')),
                ('state', localflavor.us.models.USStateField(blank=True, max_length=2, null=True, verbose_name='State')),
                ('zip_code', localflavor.us.models.USZipCodeField(blank=True, max_length=10, null=True, verbose_name='Zip Code')),
                ('host', models.CharField(default='default', max_length=100)),
            ],
            options={
                'verbose_name': 'US Location',
                'verbose_name_plural': 'US Locations',
            },
        ),
        migrations.CreateModel(
            name='BranchLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('open_to_public', models.BooleanField(default=True, help_text='Set to false if this building is staff-only or a processing center.', verbose_name='open to public')),
                ('host', models.CharField(default='default', max_length=100)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.uslocation')),
            ],
        ),
        migrations.CreateModel(
            name='AccountType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('_itemtype_checkout_limits', models.JSONField(default=dict, verbose_name='itemtype checkout limits')),
                ('_itemtype_hold_limits', models.JSONField(default=dict, verbose_name='itemtype hold limits')),
                ('checkout_limit', models.IntegerField(blank=True, default=150, help_text='How many materials total is this account type allowed to have checked out?', null=True, verbose_name='checkout limit')),
                ('hold_limit', models.IntegerField(blank=True, default=10, help_text='How many active holds is this account type allowed to have?', null=True, verbose_name='hold limit')),
                ('can_checkout_materials', models.BooleanField(default=True, help_text='Allow this account type to check out materials at all.')),
                ('allowed_item_types', models.ManyToManyField(help_text='This account type will only be allowed to check out the listed item types here. If this is empty, all item types will be allowed. Use the "Can Checkout Materials" toggle to disable all checkouts.', to='records.ItemType')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('card_number', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=50, null=True, verbose_name='title')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_minor', models.BooleanField(default=False, help_text='Check if the person this account belongs to is legally considered a minor.')),
                ('birth_year', models.IntegerField(blank=True, help_text='If allowed, enter the year of birth for the patron. Helps differentiate between patrons with the same name.', null=True, verbose_name='birth year')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user is a library staff member.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('host', models.CharField(default='default', max_length=100)),
                ('searchable_first_name', models.CharField(blank=True, max_length=150)),
                ('searchable_last_name', models.CharField(blank=True, max_length=150)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.uslocation')),
                ('default_branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_branch', to='users.branchlocation')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
                ('work_branch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='work_location', to='users.branchlocation')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'permissions': [('create_patron_account', 'Can create a patron account'), ('read_patron_account', 'Can see patron account data'), ('change_patron_account', 'Can change patron account information'), ('delete_patron_account', 'Can delete patron accounts'), ('edit_user_notes', 'Can edit user notes field'), ('create_staff_account', 'Can create a staff account'), ('read_staff_account', 'Can see staff account data'), ('change_staff_account', 'Can change staff account information'), ('delete_staff_account', 'Can delete staff accounts'), ('generate_financial_reports', 'Can generate reports with financial data'), ('generate_general_reports', 'Can generate reports on anything non-financial')],
            },
            bases=(models.Model, alexandria.searchablefields.mixins.SearchableFieldMixin),
            managers=[
                ('objects', alexandria.users.models.UserManager()),
            ],
        ),
    ]
