# ── 1. CRIAR INSTÂNCIA EC2 ──────────────────────────────────────
from services.ec2_operations import create_ec2_instance
instance_id = create_ec2_instance(instance_name='my-ec2-instance')

# Retorna: 'i-776c834b7a8f23178'

# ── 2. CRIAR A LAMBDA DE SNAPSHOT ──────────────────────────────
from services.lambda_operations import create_lambda, update_lambda_env
create_lambda(
    name='ec2-snapshot',
    source_file='services/automating_ec2_snapshot.py',
    handler='automating_ec2_snapshot.lambda_handler',
)
# Configura a Lambda para apontar para a instância criada
update_lambda_env('ec2-snapshot', {
    'INSTANCE_ID': instance_id,
})

# ── 3. CRIAR REGRA NO EVENTBRIDGE ──────────────────────────────
from services.event_bridge_operations import create_rule, add_target
create_rule(
    rule_name='ec2-snapshot-schedule',
    schedule_expression='rate(2 minutes)',
    description='Automated EC2 Snapshot',
)
# Vincula a Lambda como alvo da regra
add_target(
    rule_name='ec2-snapshot-schedule',
    target_id='ec2-snapshot-target',
    target_arn='arn:aws:lambda:us-east-1:000000000000:function:ec2-snapshot',
)

# ── 4. VERIFICAR ────────────────────────────────────────────────
from services.lambda_operations import invoke_lambda
from services.event_bridge_operations import list_rules
invoke_lambda('ec2-snapshot')   # testa a Lambda manualmente
list_rules()                    # confirma a regra ativa