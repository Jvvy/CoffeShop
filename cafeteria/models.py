from django.db import models
from django.contrib.auth.models import User


#Models para o sistema de pedidos de uma cafeteria ...:
class Pedido(models.Model):
    nome = models.CharField(max_length=255)
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo_entrega = models.CharField(  # <-- novo campo
        max_length=20,
        choices=[('retirada', 'Retirada no Local'), ('delivery', 'Tele Entrega')],
        default='retirada'
    )
    asaas_id = models.CharField(max_length=100, blank=True, null=True)
    pago = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.nome}"


#model para os itens do pedido ...:
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)  # preço unitário no momento do pedido

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"



#model para os produtos da cafeteria ...:
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)

    def __str__(self):
        return self.nome

# Model para o perfil do usuário ...:
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14)
    data_nascimento = models.DateField()
    celular = models.CharField(max_length=15)

    def __str__(self):
        return self.nome
