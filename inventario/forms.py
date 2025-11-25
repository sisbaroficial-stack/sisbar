from django import forms
from .models import Producto
from categorias.models import Categoria, Subcategoria
from proveedores.models import Proveedor


class ProductoForm(forms.ModelForm):
    """
    Formulario para crear y editar productos
    """
    
    class Meta:
        model = Producto
        fields = [
            'codigo', 'codigo_barras', 'nombre', 'descripcion',
            'categoria', 'subcategoria', 'cantidad', 'cantidad_minima',
            'unidad_medida', 'precio_compra', 'proveedor',
            'imagen', 'ubicacion'
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único del producto'
            }),
            'codigo_barras': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de barras (opcional)'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_categoria'
            }),
            'subcategoria': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_subcategoria'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'cantidad_minima': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'value': 5
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'form-select'
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'proveedor': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Estante A-3, Bodega 1'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer algunos campos opcionales
        self.fields['codigo_barras'].required = False
        self.fields['descripcion'].required = False
        self.fields['subcategoria'].required = False
        self.fields['proveedor'].required = False
        self.fields['imagen'].required = False
        self.fields['ubicacion'].required = False
        
        # Filtrar solo categorías y proveedores activos
        self.fields['categoria'].queryset = Categoria.objects.filter(activa=True)
        self.fields['proveedor'].queryset = Proveedor.objects.filter(activo=True)
        
        # Si hay una categoría seleccionada, filtrar subcategorías
        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = Subcategoria.objects.filter(
                    categoria_id=categoria_id,
                    activa=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['subcategoria'].queryset = self.instance.categoria.subcategorias.filter(
                activa=True
            )


class DescontarProductoForm(forms.Form):
    """
    Formulario para descontar productos del inventario
    """
    
    codigo = forms.CharField(
        label='Código del Producto',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Escanea o escribe el código',
            'autofocus': True
        })
    )
    
    cantidad = forms.IntegerField(
        label='Cantidad a Descontar',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '1',
            'value': 1
        })
    )
    
    motivo = forms.CharField(
        label='Motivo (Opcional)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Venta, uso interno, etc.'
        })
    )


class BuscarProductoForm(forms.Form):
    """
    Formulario de búsqueda de productos
    """
    
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código, nombre, descripción...'
        })
    )
    
    categoria = forms.ModelChoiceField(
        label='Categoría',
        queryset=Categoria.objects.filter(activa=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    estado = forms.ChoiceField(
        label='Estado',
        choices=[('', 'Todos')] + list(Producto.ESTADOS),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )