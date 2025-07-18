# your_app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from engine.pressio_engine import realizar_analise_completa


# --- VIEWS DO FLUXO DE INSERÇÃO DE DADOS ---

@login_required
def insercao(request):
    """Passo 1: Coleta dados da Grua e do Solo."""
    if request.method == 'POST':
        request.session['c'] = request.POST.get('c')
        request.session['p_tf'] = request.POST.get('p_tf')
        request.session['qa'] = request.POST.get('qa')
        return redirect('insercao_mats')
    return render(request, 'pages/insercao.html')


@login_required
def insercao_mats(request):
    """Passo 2: Coleta dados Geométricos dos Mats."""
    if request.method == 'POST':
        request.session['l_real'] = request.POST.get('l_real')
        request.session['b'] = request.POST.get('b')
        request.session['d'] = request.POST.get('d')
        return redirect('insercao_props')
    return render(request, 'pages/insercao_mats.html')


@login_required
def insercao_props(request):
    """Passo 3: Coleta dados das Propriedades Mecânicas."""
    if request.method == 'POST':
        request.session['densidade'] = request.POST.get('densidade')
        request.session['fb'] = request.POST.get('fb')
        request.session['fv'] = request.POST.get('fv')
        request.session['e_gpa'] = request.POST.get('e_gpa')
        return redirect('revisao')
    return render(request, 'pages/insercao_props.html')


# --- VIEWS DE REVISÃO E CÁLCULO ---

@login_required
def revisao_dados_view(request):
    """Passo 4: Junta todos os dados da sessão para mostrar na página de revisão."""
    context = {
        'c': request.session.get('c'),
        'p_tf': request.session.get('p_tf'),
        'qa': request.session.get('qa'),
        'l_real': request.session.get('l_real'),
        'b': request.session.get('b'),
        'd': request.session.get('d'),
        'densidade': request.session.get('densidade'),
        'fb': request.session.get('fb'),
        'fv': request.session.get('fv'),
        'e_gpa': request.session.get('e_gpa'),
    }
    return render(request, 'pages/revisao_dados.html', context)


@login_required
def calcular_view(request):
    """
    Esta view é o ponto final do fluxo. Ela é acionada pelo botão "Calcular"
    da página de revisão e executa a análise.
    """
    if request.method == 'POST':
        dados_para_engine = request.POST.dict()
        resultados = realizar_analise_completa(dados_para_engine)

        # Debug antes de salvar na sessão
        print("\n--- DEBUG NA CALCULAR_VIEW ---")
        print(resultados)
        print("------------------------------\n")

        request.session['resultados_finais'] = resultados
        return redirect('resultados')
    return redirect('insercao')


@login_required
def resultados_view(request):
    """Exibe a página final com os resultados da análise."""
    contexto_completo = request.session.get('resultados_finais', {})

    # Debug depois de ler a sessão
    print("\n--- DEBUG NA RESULTADOS_VIEW ---")
    print(contexto_completo)
    print("-------------------------------\n")

    return render(request, 'pages/resultados.html', contexto_completo)


# --- Outras Views ---

def index(request):
    return redirect('login')


def under_construction(request):
    return render(request, 'pages/under_construction.html')


def contact(request):
    """Formulário de contato público (feedback/perguntas)."""
    if request.method == 'POST':
        name    = request.POST.get('name')
        email   = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        full_message = f"From: {name} <{email}>\n\n{message}"

        send_mail(
            subject,
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_RECIPIENT_EMAIL],
            fail_silently=False,
        )
        return redirect('contact_thanks')

    return render(request, 'pages/contact.html')


def contact_thanks(request):
    """Página de agradecimento após envio do formulário de contato."""
    return render(request, 'pages/contact_thanks.html')


# A view de registro não foi fornecida, mantive placeholder:
def register_view(request):
    # Sua lógica de registro aqui
    pass
