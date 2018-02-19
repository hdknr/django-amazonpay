from django.utils import translation
import djclick as click
from amzpay import models, encoders
from logging import getLogger
log = getLogger()

translation.activate('ja')


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    pass


def to_json(call):
    return encoders.to_json(
        {'id': call.id, 'action': call.action, 'success': call.success,
         'request': call.request_object,
         'response': call.response_object,})

@main.command()
@click.argument('id')
@click.pass_context
def describe(ctx, id):
    ''' Call Detail'''
    call = models.PayCall.objects.filter(id=id).first()
    click.echo(to_json(call))


def calls(parent_model, parent_id):
    parent_model = 'pay' + parent_model

    click.echo("[")
    for call in models.PayCall.objects.filter(
            content_type__model=parent_model, object_id=parent_id):
        click.echo(to_json(call))
        click.echo(',')
    click.echo("{}]")


@main.command()
@click.argument('parent_model')
@click.argument('parent_id')
@click.pass_context
def lists(ctx, parent_model, parent_id):
    ''' Call List'''
    calls(parent_model, parent_id)
