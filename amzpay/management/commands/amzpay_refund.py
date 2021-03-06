from django.utils import translation, timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
import djclick as click
from datetime import timedelta
from amzpay import models, encoders
from logging import getLogger
log = getLogger()

translation.activate('ja')


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    pass


@main.command()
@click.argument('id')
@click.option('--client', '-c', default=None)
@click.pass_context
def refund(ctx, id, client):
    ''' Refund '''

    instance = models.PayRefund.objects.filter(id=id).first()
    if instance:
        click.echo("Refunding {}".format(instance.refund_number))
        click.echo(instance.refund().response)


@main.command()
@click.argument('id')
@click.pass_context
def update_detail(ctx, id):
    ''' Update Capture Detail'''

    instance = models.PayRefund.objects.filter(id=id).first()
    if instance:
        click.echo("Update {}".format(instance.refund_id))
        click.echo(instance.get_detail().response)


@main.command()
@click.argument('id')
@click.pass_context
def describe(ctx, id):
    ''' Refund Detail'''
    instance = models.PayRefund.objects.filter(id=id).first()
    click.echo(instance.latest.response)
