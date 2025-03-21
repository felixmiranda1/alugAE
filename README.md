# alugAE 🏠🚀

**alugAE** é uma plataforma web para **gestão de contratos de aluguel** com foco em **automação de cobranças**, **processamento de pagamentos** e **comunicação via WhatsApp**.  
Desenvolvido com **Django**, **Celery** e **Redis**, o sistema garante uma experiência simples e eficiente para **landlords** e **tenants**.

---

## ✨ Principais Funcionalidades

✅ Gestão de contratos de aluguel (Landlord e Tenant)  
✅ Cobrança automática via WhatsApp com integração Twilio  
✅ Upload e análise de comprovantes de pagamento (PIX)  
✅ Aprovação e rejeição manual de pagamentos pelos landlords  
✅ Sistema de notificações inteligente para lembretes de vencimento  
✅ Infraestrutura assíncrona com Celery e Redis para alta performance  
✅ Painel administrativo completo via Django Admin  

---

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.x  
- **Tarefas Assíncronas**: Celery 5.x  
- **Broker de Mensagens**: Redis (Railway)  
- **Agendamento de Tarefas**: Celery Beat + django-celery-beat  
- **Mensagens WhatsApp**: Twilio API  
- **Banco de Dados**: PostgreSQL  
- **Deploy**: Railway  
- **Frontend**: DaisyUI + Tailwind (versões futuras)

---

## 🚀 Instalação e Uso Local

### Pré-requisitos
- Python 3.12+
- Redis
- PostgreSQL

### Clone o Repositório
```bash
git clone https://github.com/felixmiranda1/alugAE.git
cd alugAE
