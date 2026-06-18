# Glossário jurídico embutido, extraído de duas fontes oficiais em PDF:
# 1. Siglas e Abreviaturas - Revista de Súmulas do STJ (RSSTJ, a.10, n.47, 2018)
# 2. Dicionário Jurídico - TJRJ / IdeaRio (PJERJ)
#
# Usado como base de referência para o Gemini gerar definições de glossário
# sem precisar acessar a internet (o portal.stf.jus.br bloqueia scraping).

SIGLAS_STJ = {
    "AC": "Apelação Cível",
    "Ag": "Agravo de Instrumento",
    "AgRg": "Agravo Regimental",
    "AI": "Argüição de Inconstitucionalidade",
    "APn": "Ação Penal",
    "AR": "Ação Rescisória",
    "CC": "Conflito de Competência",
    "EAC": "Embargos Infringentes em Apelação Cível",
    "EAR": "Embargos Infringentes em Ação Rescisória",
    "EAg": "Embargos de Divergência no Agravo",
    "EDcl": "Embargos de Declaração",
    "EREsp": "Embargos de Divergência em Recurso Especial",
    "ERMS": "Embargos Infringentes no Recurso em Mandado de Segurança",
    "HC": "Habeas Corpus",
    "HD": "Habeas Data",
    "HSE": "Homologação de Sentença Estrangeira",
    "IDC": "Incidente de Deslocamento de Competência",
    "Inq": "Inquérito",
    "IUJ": "Incidente de Uniformização de Jurisprudência",
    "MC": "Medida Cautelar",
    "MI": "Mandado de Injunção",
    "MS": "Mandado de Segurança",
    "PA": "Processo Administrativo",
    "Pet": "Petição",
    "QO": "Questão de Ordem",
    "Rcl": "Reclamação",
    "RE": "Recurso Extraordinário",
    "REsp": "Recurso Especial",
    "RHC": "Recurso em Habeas Corpus",
    "RHD": "Recurso em Habeas Data",
    "RMI": "Recurso em Mandado de Injunção",
    "RMS": "Recurso em Mandado de Segurança",
    "RO": "Recurso Ordinário",
    "Rp": "Representação",
    "RvCr": "Revisão Criminal",
    "S": "Súmula",
    "SEC": "Sentença Estrangeira Contestada",
    "SL": "Suspensão de Liminar",
    "SLS": "Suspensão de Liminar e de Sentença",
    "SS": "Suspensão de Segurança",
    "STA": "Suspensão de Tutela Antecipada",
}

DICIONARIO_JURIDICO = {
    "A quo": "A instância de origem onde foi dada a decisão da qual se pretende recorrer; ou data inicial da contagem de um prazo.",
    "Absolvição": "Reconhecimento da inocência de uma pessoa.",
    "Ação Judicial": "Meio processual para a defesa de um direito, levando o caso ao Poder Judiciário.",
    "Ação Penal Privada": "Ação judicial para apurar a prática de um crime, que somente pode ser proposta pela própria vítima ou seu representante legal (ex: calúnia, difamação, injúria).",
    "Ação Penal Pública": "Ação judicial para apurar a prática de um crime, que somente pode ser proposta pelo Ministério Público (ex: homicídio, estupro, roubo, furto, estelionato).",
    "Ação Rescisória": "Ação judicial que busca anular uma sentença ou acórdão já transitado em julgado.",
    "Acórdão": "Decisão final tomada por um colegiado de, no mínimo, 3 Desembargadores.",
    "Ad quem": "A instância superior a quem se recorre de uma sentença ou decisão para que seja reavaliada.",
    "Advogado Dativo": "Advogado nomeado para a defesa gratuita de quem não pode pagar por um advogado, em situações em que a Defensoria Pública não pode estar presente.",
    "Agravado": "Parte contrária àquela que apresenta o agravo.",
    "Agravante": "Parte que apresenta o agravo.",
    "Agravo de Instrumento": "Recurso apresentado ao Desembargador contra uma decisão interlocutória dada por um Juiz em um processo em andamento na 1ª instância.",
    "Agravo em Recurso Especial": "Recurso direcionado ao STJ contra decisão que inadmitiu o Recurso Especial.",
    "Agravo em Recurso Extraordinário": "Recurso direcionado ao STF contra decisão que inadmitiu o Recurso Extraordinário.",
    "Agravo Interno": "Recurso que busca a revisão de decisão monocrática dada pelo Relator, submetendo-a ao colegiado, nos casos previstos no Código de Processo Civil.",
    "Agravo Regimental": "Recurso que busca a revisão de decisão monocrática dada pelo Relator, submetendo-a ao colegiado, nos casos previstos no Regimento Interno do Tribunal.",
    "Amicus Curiae": "'Amigo da corte'. Pessoa ou organização que não é parte em um caso, mas que o tribunal permite oferecer informações ou perspectivas relevantes sobre as questões em discussão.",
    "Anulação": "Ato de invalidar uma decisão anterior, tornando-a sem efeito.",
    "Apelação": "Recurso apresentado para tentar mudar o resultado do julgamento.",
    "Apelado": "Parte contrária àquela que apresenta a apelação.",
    "Apelante": "Parte que apresenta a apelação.",
    "Apensamento": "Ato de vincular um processo a outro, para que passem a andar juntos.",
    "Ato Ordinatório": "Publicação sem conteúdo decisório que serve para movimentar o processo.",
    "Audiência de Conciliação": "Realizada entre autor e réu, intermediada por um conciliador, buscando chegar a um acordo entre as partes.",
    "Audiência de Custódia": "Realizada com pessoa presa em flagrante, apresentada a um Juiz que verifica a legalidade da prisão e sua eventual conversão em prisão preventiva ou liberdade provisória.",
    "Audiência de Instrução e Julgamento": "Realizada entre autor, réu e Juiz, quando não houve acordo. O Juiz ouve as partes, recolhe provas e decide sobre o conflito.",
    "Autor": "Parte responsável por levar uma questão à apreciação do Judiciário; quem inicia o processo.",
    "Autuação": "Conjunto de atos necessários para formar um novo processo a partir da petição inicial.",
    "Baixa à Origem": "Ocorre quando o processo é enviado à unidade onde ele foi iniciado.",
    "Bloqueio On-Line": "Ordem judicial aos bancos determinando a retenção de valor nas contas bancárias da parte devedora.",
    "Citação": "Ato processual de comunicar à parte que está sendo processada para apresentar sua defesa.",
    "Conclusão": "Ato de enviar o processo ao Magistrado para que ele avalie a questão e tome a decisão cabível.",
    "Conflito de Competência": "Ocorre quando dois ou mais Magistrados se declaram, ou não, com atribuição para julgar o mesmo processo.",
    "Contestação": "Documento pelo qual a parte ré se defende dos fatos apresentados pelo autor na petição inicial.",
    "Contrarrazões": "Documento pelo qual a parte recorrida se defende das razões alegadas no recurso.",
    "Curatela": "Instituto jurídico de proteção de pessoa interditada por incapacidade jurídica, na qual um curador administra seus bens e protege seus direitos.",
    "Dano Material": "Prejuízo financeiro causado a uma pessoa, gerando diminuição de seu patrimônio.",
    "Dano Moral": "Prejuízo emocional causado a uma pessoa, violando sua honra e dignidade.",
    "Decisão Interlocutória": "Manifestação do Magistrado sobre uma questão incidental durante o processo, sem encerrá-lo.",
    "Decisão Monocrática": "Decisão tomada por um único Magistrado.",
    "Defensoria Pública": "Órgão público que presta atendimento jurídico gratuito a quem não pode pagar por um advogado.",
    "Deferir": "Atender a um pedido; decisão favorável a quem pediu.",
    "Denegar": "Negar um pedido; decisão desfavorável a quem pediu.",
    "Denúncia": "Petição inicial da ação penal pública, feita pelo Ministério Público para pedir a condenação de uma pessoa por fato criminoso.",
    "Desembargador": "Magistrado que atua na 2ª instância do Tribunal de Justiça.",
    "Desembargador Relator": "Desembargador responsável pelo andamento do processo até o julgamento, fazendo o relatório e dando seu voto.",
    "Despacho": "Manifestação do Magistrado com as medidas necessárias para o andamento do processo.",
    "Embargos de Declaração": "Recurso dirigido ao próprio Magistrado que julgou, para esclarecer obscuridade, omissão ou contradição na decisão.",
    "Ementa": "Relatório bastante resumido do processo.",
    "Habeas Corpus": "Ação judicial que protege a liberdade de locomoção de uma pessoa, quando ameaçada ou violada por ato ilegal ou abuso de poder.",
    "Habeas Data": "Ação judicial que garante o acesso de uma pessoa a dados e informações sobre ela mesma constantes em registros públicos.",
    "Honorários Advocatícios": "Remuneração devida ao advogado pelos serviços prestados, independentemente do resultado do processo.",
    "Honorários de Sucumbência": "Valor fixado por lei a ser pago pela parte perdedora ao advogado da parte vencedora.",
    "Improcedência do Pedido": "Ocorre quando o Magistrado não aceita o pedido feito pela parte.",
    "Inadimplência": "Não cumprimento de um contrato; não pagamento da dívida no vencimento.",
    "Inquérito Policial": "Procedimento administrativo da polícia para apurar a existência de infração penal e sua autoria, embasando possível ação penal.",
    "Intimação": "Comunicação aos advogados e partes sobre alguma decisão ou ato do processo.",
    "Juiz": "Aquele com atribuição de aplicar a lei e julgar os casos na 1ª instância.",
    "Juízo de Admissibilidade": "Exame para analisar se Recursos Extraordinário, Especial ou Ordinário Constitucional reúnem os requisitos para serem remetidos ao STF ou STJ.",
    "Julgamento Monocrático": "Ocorre quando apenas um Desembargador julga o processo, sem levá-lo à sessão de julgamento.",
    "Jurisprudência": "Conjunto de decisões dadas pelo Tribunal que possuem mesma interpretação sobre o mesmo caso.",
    "Liminar": "Decisão urgente para resguardar direitos ou evitar prejuízos antes do julgamento do mérito da causa.",
    "Mandado de Prisão": "Documento determinando a prisão de uma pessoa.",
    "Mandado de Segurança": "Ação judicial que protege direito líquido e certo ameaçado ou violado por ato ilegal ou abuso de poder.",
    "Ministério Público": "Órgão público responsável por defender na Justiça os interesses da sociedade e do regime democrático.",
    "Pedido de Liminar": "Pedido para que o Magistrado conceda um direito antecipadamente, de forma provisória, por urgência e risco de perda do direito.",
    "Penhora": "Instrumento judicial para reter bens do devedor, garantindo seu uso posterior para pagamento da dívida.",
    "Petição Inicial": "Documento com o qual se inicia um processo, narrando os fatos e os pedidos do autor.",
    "Precatório Judicial": "Determinação judicial para que a Fazenda Pública pague quantia a seu credor, em razão de condenação final.",
    "Precedente": "Decisões judiciais que servem como exemplo para outros julgamentos em casos semelhantes.",
    "Preclusão": "Perda do direito de praticar um ato processual, por não ter agido no prazo legal ou por já tê-lo praticado.",
    "Prescrição": "Perda do direito de interpor uma ação quando o titular deixa de agir no prazo legal.",
    "Recorrente": "Parte que apresenta o recurso.",
    "Recorrido": "Parte contrária àquela que apresenta o recurso.",
    "Recurso Especial": "Recurso dirigido ao STJ, submetido antes a juízo de admissibilidade para verificar se reúne os requisitos necessários.",
    "Recurso Extraordinário": "Recurso dirigido ao STF, submetido antes a juízo de admissibilidade para verificar se reúne os requisitos necessários.",
    "Recurso Repetitivo": "Sistema de padronização para que Recursos Especiais sobre a mesma questão jurídica sejam julgados com a mesma interpretação (tema) fixada pelo STJ.",
    "Redistribuição": "Ocorre quando um novo Magistrado passa a ser o responsável pelo processo, substituindo o anterior.",
    "Repercussão Geral": "Sistema de padronização para que Recursos Extraordinários sobre a mesma questão constitucional sejam julgados de acordo com a interpretação (tema) fixada pelo STF.",
    "Réu": "Parte contra quem o autor demanda em um processo judicial.",
    "Revelia": "Ocorre quando o réu não se defende nem apresenta contestação no processo.",
    "Sentença": "Manifestação por escrito do Magistrado decidindo o caso na 1ª instância.",
    "STF": "Supremo Tribunal Federal, órgão máximo do Poder Judiciário brasileiro, responsável pela defesa e interpretação da Constituição.",
    "STJ": "Superior Tribunal de Justiça, conhecido como 'Tribunal da Cidadania', instância máxima na defesa e interpretação das leis federais.",
    "Súmula": "Registro das interpretações pacíficas ou majoritárias de um Tribunal.",
    "Trânsito em Julgado": "Ocorre quando uma decisão judicial se torna definitiva, sem mais possibilidade de recurso.",
    "Vara": "Repartição judiciária de 1ª instância onde o Juiz exerce suas atribuições.",
}


def buscar_termo(termo):
    """Busca um termo (sigla ou verbete) no glossário embutido.
    Retorna a definição se encontrada, ou None."""
    termo_limpo = termo.strip()

    if termo_limpo in SIGLAS_STJ:
        return SIGLAS_STJ[termo_limpo]

    if termo_limpo in DICIONARIO_JURIDICO:
        return DICIONARIO_JURIDICO[termo_limpo]

    # Busca case-insensitive como fallback
    for chave, valor in DICIONARIO_JURIDICO.items():
        if chave.lower() == termo_limpo.lower():
            return valor

    return None


def formatar_glossario_para_prompt():
    """Gera um texto formatado com todo o glossário, para incluir no prompt do Gemini."""
    linhas = ["SIGLAS E ABREVIATURAS (fonte: Revista de Súmulas do STJ):"]
    for sigla, significado in SIGLAS_STJ.items():
        linhas.append(f"- {sigla}: {significado}")

    linhas.append("\nDICIONÁRIO JURÍDICO (fonte: TJRJ/PJERJ):")
    for termo, definicao in DICIONARIO_JURIDICO.items():
        linhas.append(f"- {termo}: {definicao}")

    return "\n".join(linhas)
