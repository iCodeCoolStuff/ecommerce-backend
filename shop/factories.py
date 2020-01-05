import os
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

from django.core.files import File
import factory

from .models import Product, ImageSet


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('word', ext_word_list=None)
    price = factory.Faker('pydecimal', positive=True, min_value=1.00, right_digits=2, max_value=1000.00)
    list_price = factory.Faker('pydecimal', positive=True, min_value=1.00, right_digits=2, max_value=1000.00)
    description = factory.Faker('paragraph', nb_sentences=12, variable_nb_sentences=True)
    featured = factory.Faker('pybool')
    new = factory.Faker('pybool')
    on_sale = factory.Faker('pybool')
    category = factory.Faker('pyint', min_value=1, max_value=4)

    #imageset = factory.RelatedFactory('shop.factories.ImageSetFactory', 'product')


class ImageSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageSet

    product = None
    img100x100 = factory.django.ImageField()
    img690x400 = factory.django.ImageField(width=690, height=400)
    img1920x1080 = factory.django.ImageField(width=1920, height=1080)

    @factory.post_generation
    def images(obj, create, extracted, **kwargs):
        if not create:
            return

        # code needs to be sped up by a LOT but most of the slowness is due to urllib ¯\_(ツ)_/¯
        img100x100 = NamedTemporaryFile(delete=True)
        img690x400 = NamedTemporaryFile(delete=True)
        img1920x1080 = NamedTemporaryFile(delete=True)

        img100x100.write(urlopen(f'http://placehold.it/100x100?text={obj.product.name}').read())
        img690x400.write(urlopen(f'http://placehold.it/690x400?text={obj.product.name}').read())
        img1920x1080.write(urlopen(f'http://placehold.it/1920x1080?text={obj.product.name}').read())

        img100x100.flush()
        img690x400.flush()
        img1920x1080.flush()

        obj.img100x100.save(os.path.basename(obj.img100x100.url), File(img100x100))
        obj.img690x400.save(os.path.basename(obj.img690x400.url), File(img690x400))
        obj.img1920x1080.save(os.path.basename(obj.img1920x1080.url), File(img1920x1080))

        obj.save()