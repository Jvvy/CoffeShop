from django.db import models



#Models para o sistema de pedidos de uma cafeteria ...:
class Pedido(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

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