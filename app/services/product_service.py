"""
Product service layer for OHMEALS.
"""
from app.extensions import db
from app.models.product import Product, ProductVariant, ProductImage

def get_all_products(include_inactive=False):
    """Get all products with their variants and images."""
    if include_inactive:
        products = Product.query.all()
    else:
        products = Product.query.filter_by(is_active=True).all()
    
    result = [p.to_dict() for p in products]
    
    if include_inactive:
        for p_obj, p_dict in zip(products, result):
            p_dict['is_active'] = p_obj.is_active
            
    return result

def create_product(data):
    """Create new product with variants and images."""
    new_product = Product(
        name=data['name'],
        description=data.get('description'),
        category=data['category'],
        taste=data.get('taste'),
        image=data.get('image'),
        video_url=data.get('video_url'),
        is_active=True,
        discount=float(data.get('discount', 0) or 0)
    )
    db.session.add(new_product)
    db.session.flush() # Get ID before commit if needed

    # Create variant
    variant_name = data.get('variant_name')
    if variant_name:
        price = float(data['price'])
        variant = ProductVariant(
            variant_name=variant_name,
            price=price,
            unit=data.get('unit', 'piece'),
            is_default=True,
            position=1,
            product_id=new_product.id,
            stock_quantity=int(data.get('stock_quantity', 100)),
            track_stock=bool(data.get('track_stock', True))
        )
        db.session.add(variant)

    # Create images
    images_data = data.get('images', [])
    for idx, img_data in enumerate(images_data):
        img_url = img_data if isinstance(img_data, str) else img_data.get('image_url', '')
        if img_url:
            new_img = ProductImage(
                product_id=new_product.id,
                image_url=img_url,
                position=idx + 1,
                is_primary=(idx == 0)
            )
            db.session.add(new_img)

    # If no gallery images but legacy image field, create one entry
    if not images_data and data.get('image'):
        new_img = ProductImage(
            product_id=new_product.id,
            image_url=data['image'],
            position=1,
            is_primary=True
        )
        db.session.add(new_img)

    db.session.commit()
    return new_product

def update_product(product_id, data):
    """Update product info, variants, images, and video."""
    product = Product.query.get_or_404(product_id)

    if 'name' in data: product.name = data['name']
    if 'description' in data: product.description = data['description']
    if 'category' in data: product.category = data['category']
    if 'taste' in data: product.taste = data['taste']
    if 'video_url' in data:
        product.video_url = data.get('video_url') or None
    if 'discount' in data:
        product.discount = float(data.get('discount', 0) or 0)
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])

    # Update variants
    if data.get('variants'):
        for vdata in data['variants']:
            if vdata.get('id'):
                variant = ProductVariant.query.get(vdata['id'])
                if variant:
                    if 'variant_name' in vdata: variant.variant_name = vdata['variant_name']
                    if 'unit' in vdata: variant.unit = vdata['unit']
                    if 'price' in vdata and vdata['price'] is not None:
                        variant.price = float(vdata['price'])
                    if 'is_available' in vdata: variant.is_available = vdata['is_available']
                    if 'is_default' in vdata: variant.is_default = vdata['is_default']
                    if 'position' in vdata: variant.position = vdata['position']
                    if 'stock_quantity' in vdata:
                        variant.stock_quantity = int(vdata['stock_quantity'])
                    if 'track_stock' in vdata:
                        variant.track_stock = bool(vdata['track_stock'])
            else:
                new_variant = ProductVariant(
                    product_id=product.id,
                    variant_name=vdata['variant_name'],
                    unit=vdata['unit'],
                    price=float(vdata['price']),
                    is_available=vdata.get('is_available', True),
                    is_default=vdata.get('is_default', False),
                    position=vdata.get('position', 0),
                    stock_quantity=int(vdata.get('stock_quantity', 100)),
                    track_stock=bool(vdata.get('track_stock', True))
                )
                db.session.add(new_variant)

    # Update images (replace all if 'images' key present)
    if 'images' in data:
        # Delete existing images
        ProductImage.query.filter_by(product_id=product.id).delete()
        # Add new images
        for idx, img_data in enumerate(data['images']):
            img_url = img_data if isinstance(img_data, str) else img_data.get('image_url', '')
            is_primary = img_data.get('is_primary', False) if isinstance(img_data, dict) else (idx == 0)
            if img_url:
                new_img = ProductImage(
                    product_id=product.id,
                    image_url=img_url,
                    position=idx + 1,
                    is_primary=is_primary
                )
                db.session.add(new_img)
        # Update legacy image field with primary
        primary_imgs = [i for i in data['images'] if (isinstance(i, dict) and i.get('is_primary'))]
        if primary_imgs:
            product.image = primary_imgs[0].get('image_url', '') if isinstance(primary_imgs[0], dict) else primary_imgs[0]
        elif data['images']:
            first = data['images'][0]
            product.image = first.get('image_url', '') if isinstance(first, dict) else first

    db.session.commit()
    return product

def delete_product(product_id):
    """Delete product and all its variants."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return True
