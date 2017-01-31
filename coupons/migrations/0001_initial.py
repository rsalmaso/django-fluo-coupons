# Copyright (C) 2016-2017, Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2013, byteweaver
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of django-coupons nor the names of its contributors may
#       be used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import django.db.models.deletion
import django.utils.timezone
import fluo.db.models.fields
from coupons.settings import COUPON_TYPES
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name_plural': 'Campaigns',
                'ordering': ['name'],
                'verbose_name': 'Campaign',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', fluo.db.models.fields.CreationDateTimeField(blank=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('last_modified_at', fluo.db.models.fields.ModificationDateTimeField(blank=True, default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('value', models.IntegerField(help_text='Arbitrary coupon value', verbose_name='Value')),
                ('code', models.CharField(blank=True, help_text='Leaving this field empty will generate a random code.', max_length=30, unique=True, verbose_name='Code')),
                ('type', models.CharField(max_length=20, choices=COUPON_TYPES, verbose_name='Type')),
                ('user_limit', models.PositiveIntegerField(default=1, verbose_name='User limit')),
                ('valid_from', models.DateTimeField(blank=True, help_text='Coupons are valid from this date', null=True, verbose_name='Valid from')),
                ('valid_until', models.DateTimeField(blank=True, help_text='Coupons expire at this date', null=True, verbose_name='Valid until')),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to='coupons.Campaign', verbose_name='Campaign')),
            ],
            options={
                'verbose_name_plural': 'Coupons',
                'ordering': ['created_at'],
                'verbose_name': 'Coupon',
            },
        ),
        migrations.CreateModel(
            name='CouponUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redeemed_at', models.DateTimeField(blank=True, null=True, verbose_name='Redeemed at')),
                ('source_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='source id')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='coupons.Coupon', verbose_name='Coupon')),
                ('source_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType', verbose_name='source content type')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name_plural': 'Coupons',
                'verbose_name': 'Coupon',
            },
        ),
    ]
