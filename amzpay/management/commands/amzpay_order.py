from django.utils import translation, timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
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
@click.argument('order_id')
@click.pass_context
def authorize(ctx, order_id):
    ''' Authorize Order'''
    order = models.PayOrder.objects.filter(id=order_id).first()
    auth = order.create_auth()
    response = auth.authorize().response_object
    click.echo(encoders.to_json(
        {'id': auth.id, 'authorization_id': auth.authorization_id}))
    click.echo(encoders.to_json(response, indent=2))


@main.command()
@click.argument('order_id')
@click.pass_context
def update_detail(ctx, order_id):
    ''' Order Detail'''
    order = models.PayOrder.objects.filter(id=order_id).first()
    click.echo(order.get_detail().response)


@main.command()
@click.argument('order_id')
@click.option('--reason', '-r', default='close')
@click.pass_context
def close(ctx, order_id, reason):
    ''' Close Order'''
    order = models.PayOrder.objects.filter(id=order_id).first()
    if order:
        click.echo("Closing {}".format(order.order_reference_id))
        click.echo(order.close(reason=reason).response)


@main.command()
@click.argument('call_id')
@click.pass_context
def call(ctx, call_id):
    ''' Order Call Detail'''
    call = models.PayOrderCall.objects.filter(id=call_id).first()
    click.echo(encoders.to_json(
        {'action': call.action, 'success': call.success,
         'request': call.request_object,
         'response': call.response_object,}))


@main.command()
@click.argument('order_id')
@click.pass_context
def describe(ctx, order_id):
    ''' Order Detail'''
    order = models.PayOrder.objects.filter(id=order_id).first()
    click.echo(order.latest.response)


@main.command()
@click.argument('order_id')
@click.pass_context
def destination(ctx, order_id):
    ''' Order Customer Destination'''
    order = models.PayOrder.objects.filter(id=order_id).first()
    click.echo(encoders.to_json(
        order.destination, indent=2, ensure_ascii=False))
