from django import template

register = template.Library()

@register.filter
def turma_has_horarios_completos(turma):
    horarios_turma = turma.horarios.all()
    sistemas_turma = turma.sistemas.all()

    for hora in horarios_turma:
        for sistema in sistemas_turma:
            if sistema.hora == hora:
                break
        else:
            # Se nenhum sistema corresponder à hora, então não está completo
            return False

    return True