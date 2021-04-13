# Generated by Django 3.1 on 2021-04-12 17:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


def forwards_func(apps, schema_editor):
    Response = apps.get_model('survey', 'Response')
    db_alias = schema_editor.connection.alias

    response_list = Response.objects.using(db_alias).all()
    for response in response_list:
        response.public_id = uuid.uuid4()
    Response.objects.using(db_alias).bulk_update(response_list, ['public_id'])

class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20210323_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False), # Why does this only create one value for all table rows?
            #field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.RunPython(
            code=forwards_func,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='response',
            name='public_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='animeresponse',
            name='anime',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='survey.anime'),
        ),
        migrations.AlterField(
            model_name='animeresponse',
            name='expectations',
            field=models.CharField(blank=True, choices=[(None, 'Met expectations / no answer'), ('S', 'Surprise'), ('D', 'Disappointment')], max_length=1),
        ),
        migrations.AlterField(
            model_name='animeresponse',
            name='response',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='survey.response'),
        ),
        migrations.AlterField(
            model_name='response',
            name='survey',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='survey.survey'),
        ),
    ]
