from django.utils import translation, timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
import djclick as click
from datetime import timedelta
from amzpay import models, encoders
from . import amzpay_call
from logging import getLogger
log = getLogger()

translation.activate('ja')


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    pass


@main.command()
@click.argument('id')
@click.pass_context
def authorize(ctx, id):
    ''' Authorize Order'''
    order = models.PayOrder.objects.filter(id=id).first()
    auth = order.create_auth()
    response = auth.authorize().response_object
    click.echo(encoders.to_json(
        {'id': auth.id, 'authorization_id': auth.authorization_id}))
    click.echo(encoders.to_json(response, indent=2))


@main.command()
@click.argument('id')
@click.pass_context
def get_detail(ctx, id):
    ''' Get Order Detail'''
    order = models.PayOrder.objects.filter(id=id).first()
    click.echo(order.get_detail().response)


@main.command()
@click.argument('id')
@click.pass_context
def set_detail(ctx, id):
    ''' Set Order Detail'''
    order = models.PayOrder.objects.filter(id=id).first()
    click.echo(order.set_detail().response)


@main.command()
@click.argument('id')
@click.option('--reason', '-r', default='close')
@click.pass_context
def close(ctx, id, reason):
    ''' Close Order'''
    order = models.PayOrder.objects.filter(id=id).first()
    if order:
        click.echo("Closing {}".format(order.order_reference_id))
        click.echo(order.close(reason=reason).response)


@main.command()
@click.argument('id')
@click.pass_context
def confirm(ctx, id):
    ''' Confirm Order'''
    # https://pay.amazon.com/jp/developer/documentation/apireference/201751980
    order = models.PayOrder.objects.filter(id=id).first()
    order and order.confirm()


@main.command()
@click.argument('id')
@click.pass_context
def calls(ctx, id):
    ''' Order Call Detail'''
    amzpay_call.calls('order', id)


@main.command()
@click.argument('id')
@click.pass_context
def describe(ctx, id):
    ''' Order Detail'''
    order = models.PayOrder.objects.filter(id=id).first()
    click.echo(order.latest.response)


@main.command()
@click.argument('id')
@click.pass_context
def destination(ctx, id):
    ''' Order Customer Destination'''
    order = models.PayOrder.objects.filter(id=id).first()
    click.echo(encoders.to_json(
        order.destination, indent=2, ensure_ascii=False))
