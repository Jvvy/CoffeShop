def total_itens_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    total = sum(carrinho.values())
    return {'total_itens_carrinho': total}
