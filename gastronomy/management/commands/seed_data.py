"""
Command para poblar la base de datos con datos de prueba completos de Nicaragua.

Uso:
    python manage.py seed_data
    python manage.py seed_data --fresh  # Limpia y vuelve a poblar
"""
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from users.models import User, VerificationRequest
from gastronomy.models import Department, TraditionalFood, FoodCollection, GastronomicRoute
from business.models import Business, BusinessMenuItem, BusinessQualification, RouteBusiness


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de prueba auténticos de Nicaragua para Xiri'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fresh',
            action='store_true',
            help='Elimina los datos previos antes de volver a sembrar',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['fresh']:
            self.stdout.write(self.style.WARNING('Limpiando datos previos...'))
            BusinessQualification.objects.all().delete()
            FoodCollection.objects.all().delete()
            RouteBusiness.objects.all().delete()
            BusinessMenuItem.objects.all().delete()
            Business.objects.all().delete()
            VerificationRequest.objects.all().delete()
            GastronomicRoute.objects.all().delete()
            TraditionalFood.objects.all().delete()
            Department.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Datos anteriores eliminados.'))

        self.stdout.write('\n1. Creando departamentos de Nicaragua con coordenadas GPS...')
        departments = self.create_departments()

        self.stdout.write('\n2. Creando platillos típicos tradicionales...')
        foods = self.create_traditional_foods(departments)

        self.stdout.write('\n3. Creando usuarios de prueba (Admin, Dueños, Turistas)...')
        users = self.create_users()

        self.stdout.write('\n4. Creando solicitudes de verificación...')
        self.create_verification_requests(users)

        self.stdout.write('\n5. Creando negocios representativos...')
        businesses = self.create_businesses(users)

        self.stdout.write('\n6. Creando platillos en el menú con precios...')
        self.create_menu_items(businesses, foods)

        self.stdout.write('\n7. Creando rutas gastronómicas y asignando negocios...')
        self.create_gastronomic_routes(departments, businesses)

        self.stdout.write('\n8. Creando calificaciones y reseñas con fotos de evidencia...')
        self.create_qualifications(users, businesses)

        self.stdout.write('\n9. Creando colección de platillos y progreso del álbum...')
        self.create_food_collections(users, foods)

        self.stdout.write(self.style.SUCCESS('\n======================================================'))
        self.stdout.write(self.style.SUCCESS(' ¡Datos de prueba de Nicaragua cargados con éxito!'))
        self.stdout.write(self.style.SUCCESS('======================================================'))
        self.stdout.write('Cuentas creadas para testing:')
        self.stdout.write('  - Admin:       admin@xiri.com      / admin1234 (Rol: admin)')
        self.stdout.write('  - Dueño 1:     dueno@xiri.com      / dueno1234 (Rol: owner - Don Pedro)')
        self.stdout.write('  - Dueña 2:     duena@xiri.com      / duena1234 (Rol: owner - Doña María)')
        self.stdout.write('  - Turista:     turista@xiri.com    / turista1234 (Rol: user - Juan)')
        self.stdout.write('  - Solicitante: solicitante@xiri.com / solicitante1234 (Rol: user - Carlos)')
        self.stdout.write('======================================================\n')

    def create_departments(self):
        """Crea los 17 departamentos/regiones de Nicaragua con datos limpios y coordenadas."""
        departments_data = [
            {"name": "Boaco", "latitude": 12.4729, "longitude": -85.6604,
             "description": "Tierra de encantadores paisajes montañosos, ganadería de altura y rica cuajada."},
            {"name": "Carazo", "latitude": 11.9103, "longitude": -86.2102,
             "description": "Famoso por su clima fresco, festividades de San Sebastián, ajiaco y dulces típicos."},
            {"name": "Chinandega", "latitude": 12.6298, "longitude": -87.1318,
             "description": "Cálida tierra volcánica del pacífico norte, mariscos, caña y dulces tradicionales."},
            {"name": "Chontales", "latitude": 11.9385, "longitude": -85.1677,
             "description": "Cuna ganadera de Nicaragua, famosa por sus quesillos, carnes y derivados lácteos."},
            {"name": "Estelí", "latitude": 13.0852, "longitude": -86.3533,
             "description": "El diamante de las Segovias, famoso por sus puros, murales y desayunos norteños."},
            {"name": "Granada", "latitude": 11.9294, "longitude": -85.9566,
             "description": "La Gran Sultana colonial a orillas del Gran Lago, cuna indiscutible del vigorón."},
            {"name": "Jinotega", "latitude": 13.1042, "longitude": -86.0024,
             "description": "La ciudad de las brumas, cuna del mejor café de altura y deliciosas güirilas."},
            {"name": "León", "latitude": 12.4382, "longitude": -86.8784,
             "description": "Ciudad universitaria y poética, hogar del nacatamal leones y quesillos en Nagarote."},
            {"name": "Madriz", "latitude": 13.3391, "longitude": -86.5204,
             "description": "Hogar del imponente Cañón de Somoto y las inconfundibles rosquillas somoteñas."},
            {"name": "Managua", "latitude": 12.1150, "longitude": -86.2362,
             "description": "La capital vibrante, famosa por sus fritangas nocturnas y vida gastronómica activa."},
            {"name": "Masaya", "latitude": 11.9738, "longitude": -86.0964,
             "description": "Capital del folclore nacional y artesanal, célebre por su sabroso vaho y cajetas."},
            {"name": "Matagalpa", "latitude": 12.9254, "longitude": -85.9189,
             "description": "La perla del septentrión, tierra del indio viejo, café aromático y clima templado."},
            {"name": "Nueva Segovia", "latitude": 13.6552, "longitude": -86.1184,
             "description": "Pinorescas montañas fronterizas con rica herencia culinaria a base de maíz criollo."},
            {"name": "Río San Juan", "latitude": 11.4088, "longitude": -84.8380,
             "description": "Santuario tropical y fluvial, hogar del sábalo real y pescados de río y lago."},
            {"name": "Rivas", "latitude": 11.4373, "longitude": -85.7136,
             "description": "Encrucijada del istmo con playas de surf y rica tradición de mariscos y dulces."},
            {"name": "Costa Caribe Norte", "latitude": 13.2541, "longitude": -84.8380,
             "description": "Región autónoma de tradición miskita y mayangna, rica en plátanos verdes y coco."},
            {"name": "Costa Caribe Sur", "latitude": 12.1389, "longitude": -83.7030,
             "description": "Tierra criolla y afrodescendiente en Bluefields, cuna del rondón, patí y pan de coco."},
        ]

        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.update_or_create(
                name=dept_data["name"],
                defaults={
                    "description": dept_data["description"],
                    "latitude": Decimal(str(dept_data["latitude"])),
                    "longitude": Decimal(str(dept_data["longitude"])),
                }
            )
            departments[dept.name] = dept
            self.stdout.write(f'  ✓ {dept.name}')

        return departments

    def create_traditional_foods(self, departments):
        """Crea platillos típicos auténticos con su departamento de origen correcto."""
        foods_data = [
            # Granada
            {"name": "Vigorón Granadino", "department": "Granada",
             "description": "Yuca cocida suave con chicharrón crocante de faja y ensalada de mamey y tomate en hoja de plátano.",
             "cultural_origin": "Nacido en 1914 en Granada por la famosa 'Loca Ramona', símbolo gastronómico por excelencia.",
             "image": "platillos/vigoron-mixto_web.jpg.webp"},

            # León
            {"name": "Nacatamal Leones", "department": "León",
             "description": "Masa de maíz criollo perfumada con achiote y manteca, rellena de cerdo marinado, arroz, papa y yerbabuena en hoja de chagüite.",
             "cultural_origin": "Platillo prehispánico perfeccionado en la época colonial, tradición de los domingos nicaragüenses.",
             "image": "platillos/nacatamal.avif"},
            {"name": "Quesillo de Nagarote", "department": "León",
             "description": "Tortilla caliente recién salida del comal con queso hilado tierno, cebollita encurtida en vinagre y abundante crema agria.",
             "cultural_origin": "Platillo típico creado en Nagarote y La Paz Centro a mediados del siglo XX por vendedoras de trenes.",
             "image": "platillos/quesillo.jpg"},

            # Masaya
            {"name": "Vaho Tradicional", "department": "Masaya",
             "description": "Carne de res cecina marinada con naranja agria, cocida al vapor sobre capas de yuca y plátano maduro envuelta en hojas de plátano.",
             "cultural_origin": "Herencia campesina de Masaya donde el vapor concentra los sabores dulces y salados.",
             "image": "platillos/vaho.jpeg"},
            {"name": "Montucas de Maíz", "department": "Masaya",
             "description": "Tamalitos de maíz tierno con relleno sazonado de pollo o cerdo, con un toque ligeramente dulzón.",
             "cultural_origin": "Elaboración ancestral de los pueblos originarios de Masaya para festividades patronales.",
             "image": "platillos/montuca.jpeg"},

            # Managua
            {"name": "Fritanga Managüense", "department": "Managua",
             "description": "Carne de res asada al carbón acompañada de gallopinto fresco, tajadas verdes crocantes y queso frito nica.",
             "cultural_origin": "Icono de las noches urbanas de Managua en cada esquina de barrio y rotonda.",
             "image": "platillos/carne-asada.jpeg"},
            {"name": "Arroz a la Valenciana Nica", "department": "Managua",
             "description": "Arroz criollo con pollo deshilachado, chorizo criollo, jamón, chícharos, salsa de tomate y mantequilla.",
             "cultural_origin": "Adaptación nicaragüense festiva de la paella española, infaltable en cumpleaños y celebraciones.",
             "image": "platillos/arroz-valen.jpeg"},

            # Matagalpa
            {"name": "Indio Viejo Matagalpino", "department": "Matagalpa",
             "description": "Guiso de masa de maíz condimentado con yerbabuena, achiote, cebolla y carne de res deshilachada en naranja agria.",
             "cultural_origin": "Plato prehispánico legendario de las tribus indígenas del norte de Nicaragua.",
             "image": "platillos/indio.jpeg"},

            # Madriz
            {"name": "Rosquillas de Somoto", "department": "Madriz",
             "description": "Horneadas crocantes de masa de maíz selecto con cuajada fresca y queso seco de la más alta calidad.",
             "cultural_origin": "Reconocidas nacional e internacionalmente como el mayor orgullo culinario de Somoto.",
             "image": "platillos/tortillas.jpg"},

            # Estelí
            {"name": "Desayuno Tres Golpes Norteño", "department": "Estelí",
             "description": "Huevos criollos fritos, gallopinto montañero, tajadas de plátano maduro o verde y abundante queso frito.",
             "cultural_origin": "El desayuno energético por excelencia del campesino norteño de las Segovias.",
             "image": "platillos/tres-g.jpg"},
            {"name": "Pinolillo y Pinol Tradicional", "department": "Estelí",
             "description": "Bebida ancestral de maíz blanco tostado y cacao molido con especias como canela y pimienta de chapa.",
             "cultural_origin": "Bebida que dio al pueblo nicaragüense el apelativo cariñoso de 'Pinoleros'.",
             "image": "platillos/pinol.jpeg"},

            # Costa Caribe Sur
            {"name": "Rondón de Mariscos Caribeño", "department": "Costa Caribe Sur",
             "description": "Sopa reconfortante con leche de coco pura, pescado fresco, camarones, langosta, yuca, malanga y plátano verde.",
             "cultural_origin": "Plato insigne afrocaribeño (Run Down) de los pescadores de Bluefields y Corn Island.",
             "image": "platillos/RONDON.jpg"},
            {"name": "Patí Bluefileño", "department": "Costa Caribe Sur",
             "description": "Empanada hojaldrada rellena de carne de res molida sazonada con chile cabro, cebolla y especias del caribe.",
             "cultural_origin": "Bocadillo caribeño tradicional de origen jamaiquino adaptado en la costa este.",
             "image": "platillos/pati.jpg"},

            # Costa Caribe Norte
            {"name": "Guabul Misquito", "department": "Costa Caribe Norte",
             "description": "Bebida tradicional a base de plátano verde madurado cocido, leche de vaca y leche de coco.",
             "cultural_origin": "Bebida típica cotidiana de la comunidad indígena miskita en Bilwi.",
             "image": "platillos/guabul.webp"},

            # Chinandega
            {"name": "Pescado Frito Tipitapa", "department": "Chinandega",
             "description": "Pescado entero frito crocante bañado en una abundante salsa criolla de tomates frescos, cebolla y chiltoma.",
             "cultural_origin": "Tradición costera del pacífico nicaragüense preferida por locales y turistas.",
             "image": "platillos/images.jpeg"},
            {"name": "Sopa de Queso Cuaresmeña", "department": "Chinandega",
             "description": "Caldo enriquecido con masa y tortas fritas de queso seco, aromatizado con hierbabuena y cebolla.",
             "cultural_origin": "Platillo esencial de la Semana Santa y Cuaresma nicaragüense.",
             "image": "platillos/sopa-queso.jpg"},

            # Carazo
            {"name": "Cajetas de Leche y Frutas", "department": "Carazo",
             "description": "Dulces tradicionales elaborados artesanalmente con leche fresca, frutas de la región y azúcar de caña.",
             "cultural_origin": "Tradición centenaria de las familias dulceras de Carazo y Diriamba.",
             "image": "platillos/cajeta_leche.webp"},

            # Boaco
            {"name": "Pollo Asado al Carbón", "department": "Boaco",
             "description": "Pollo marinado con cítricos y especias nativas, asado lentamente sobre brasas de leña aromática.",
             "cultural_origin": "Comida de campo tradicional en las haciendas ganaderas boaqueñas.",
             "image": "platillos/pollo-carbon.jpeg"},

            # Río San Juan
            {"name": "Sopa de Mondongo", "department": "Río San Juan",
             "description": "Sopa sustanciosa a base de toalla de res con verduras tropicales como chayote, elote, yuca y repollo.",
             "cultural_origin": "Platillo dominguero y festivo característico de las riberas del Río San Juan.",
             "image": "platillos/mondongo.jpg"},

            # Rivas
            {"name": "Arroz con Leche Casero", "department": "Rivas",
             "description": "Postre cremoso de arroz cocido en leche fresca con canela, pasas y un toque de vainilla dulce.",
             "cultural_origin": "Postre de herencia colonial presente en todas las casas del pacífico sur.",
             "image": "platillos/arroz-leche.jpg"},

            # Nueva Segovia
            {"name": "Pupusas Segovianas", "department": "Nueva Segovia",
             "description": "Tortillas gruesas de maíz rellenas con abundante queso quesillo fundido, frijoles y chicharrón molido.",
             "cultural_origin": "Influencia compartida en la frontera norteña con un toque particular nicaragüense.",
             "image": "platillos/pupusa.webp"},
        ]

        foods = {}
        for food_data in foods_data:
            dept = departments.get(food_data["department"])
            if dept:
                food, created = TraditionalFood.objects.update_or_create(
                    name=food_data["name"],
                    defaults={
                        "description": food_data["description"],
                        "cultural_origin": food_data["cultural_origin"],
                        "department_origin": dept,
                        "image": food_data["image"],
                    }
                )
                foods[food.name] = food
                self.stdout.write(f'  ✓ {food.name} ({dept.name})')

        return foods

    def create_users(self):
        """Crea usuarios para cada rol del sistema con credenciales estandarizadas."""
        users_data = [
            {
                "username": "admin",
                "email": "admin@xiri.com",
                "password": "admin1234",
                "first_name": "Administrador",
                "last_name": "Xiri",
                "rol": "admin",
                "contact_number": "+50588880000",
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "don_pedro",
                "email": "dueno@xiri.com",
                "password": "dueno1234",
                "first_name": "Pedro",
                "last_name": "Gutiérrez",
                "rol": "owner",
                "contact_number": "+50588887777",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "dona_maria",
                "email": "duena@xiri.com",
                "password": "duena1234",
                "first_name": "María",
                "last_name": "López",
                "rol": "owner",
                "contact_number": "+50589996666",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "turista_juan",
                "email": "turista@xiri.com",
                "password": "turista1234",
                "first_name": "Juan",
                "last_name": "Pérez",
                "rol": "user",
                "contact_number": "+50587775555",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "carlos_aspira",
                "email": "solicitante@xiri.com",
                "password": "solicitante1234",
                "first_name": "Carlos",
                "last_name": "Mendoza",
                "rol": "user",
                "contact_number": "+50586664444",
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        users = {}
        for udata in users_data:
            user, created = User.objects.get_or_create(
                username=udata["username"],
                defaults={
                    "email": udata["email"],
                    "first_name": udata["first_name"],
                    "last_name": udata["last_name"],
                    "rol": udata["rol"],
                    "contact_number": udata["contact_number"],
                    "is_staff": udata["is_staff"],
                    "is_superuser": udata["is_superuser"],
                }
            )
            user.set_password(udata["password"])
            user.email = udata["email"]
            user.rol = udata["rol"]
            user.is_staff = udata["is_staff"]
            user.is_superuser = udata["is_superuser"]
            user.save()
            users[user.username] = user
            self.stdout.write(f'  ✓ {user.username} ({user.rol}) -> {user.email}')

        return users

    def create_verification_requests(self, users):
        """Crea solicitudes en cada estado ('pending', 'approved', 'rejected') para pruebas."""
        requests_data = [
            {
                "user": users["carlos_aspira"],
                "business_name": "Comidería y Asados Monimbó",
                "business_address": "Barrio Monimbó, del Colegio 2 c. al este, Masaya",
                "id_card_number": "4011205900001A",
                "state": "pending",
                "check_by": None,
                "reviews": None,
            },
            {
                "user": users["don_pedro"],
                "business_name": "Fritanga y Asados Managüenses",
                "business_address": "Rotonda Bello Horizonte, 1 c. al sur, Managua",
                "id_card_number": "0012010850002B",
                "state": "approved",
                "check_by": users["admin"],
                "reviews": "Documentación en regla, negocio verificado.",
            },
            {
                "user": users["turista_juan"],
                "business_name": "Kiosko Rápido El Parque",
                "business_address": "Parque Central de Jinotepe",
                "id_card_number": "0410504950003C",
                "state": "rejected",
                "check_by": users["admin"],
                "reviews": "Foto de cédula borrosa e ilegible. Favor subir fotografía nítida del documento original.",
            }
        ]

        for req_data in requests_data:
            req, created = VerificationRequest.objects.update_or_create(
                user=req_data["user"],
                business_name=req_data["business_name"],
                defaults={
                    "business_address": req_data["business_address"],
                    "id_card_number": req_data["id_card_number"],
                    "identity_document": "documents/id_cards/cedula_sample.jpeg",
                    "state": req_data["state"],
                    "check_by": req_data["check_by"],
                    "reviews": req_data["reviews"],
                }
            )
            self.stdout.write(f'  ✓ Solicitud: {req.business_name} [{req.state}]')

    def create_businesses(self, users):
        """Crea negocios gastronómicos auténticos con coordenadas GPS reales."""
        businesses_data = [
            {
                "name": "El Kiosko del Vigorón de Doña Vilma",
                "contact_number": "+50589996666",
                "address": "Costado Sur del Parque Central, Granada",
                "latitude": Decimal("11.929800"),
                "longitude": Decimal("-85.956000"),
                "owner": users["dona_maria"],
            },
            {
                "name": "Quesillos Mi Bohío Nagarote",
                "contact_number": "+50588887777",
                "address": "Km 41 Carretera Nueva a León, Nagarote",
                "latitude": Decimal("12.268000"),
                "longitude": Decimal("-86.615000"),
                "owner": users["don_pedro"],
            },
            {
                "name": "Fritanga y Asados Managüenses",
                "contact_number": "+50588887777",
                "address": "Rotonda Bello Horizonte, 1 c. al sur, Managua",
                "latitude": Decimal("12.146500"),
                "longitude": Decimal("-86.230100"),
                "owner": users["don_pedro"],
            },
            {
                "name": "El Rincón de las Rosquillas Somoteñas",
                "contact_number": "+50589996666",
                "address": "Frente a la Parroquia Santiago, Somoto, Madriz",
                "latitude": Decimal("13.483300"),
                "longitude": Decimal("-86.583300"),
                "owner": users["dona_maria"],
            },
            {
                "name": "Sabor Caribeño y Rondón de Bluefields",
                "contact_number": "+50588887777",
                "address": "Barrio Punta Fría, frente al muelle, Bluefields",
                "latitude": Decimal("12.013500"),
                "longitude": Decimal("-83.763500"),
                "owner": users["don_pedro"],
            },
        ]

        businesses = {}
        for bdata in businesses_data:
            biz, created = Business.objects.update_or_create(
                name=bdata["name"],
                defaults={
                    "contact_number": bdata["contact_number"],
                    "address": bdata["address"],
                    "latitude": bdata["latitude"],
                    "longitude": bdata["longitude"],
                    "owner": bdata["owner"],
                }
            )
            businesses[biz.name] = biz
            self.stdout.write(f'  ✓ Negocio: {biz.name} (Dueño: {biz.owner.username})')

        return businesses

    def create_menu_items(self, businesses, foods):
        """Crea platillos en el menú de cada negocio con precios y variantes tradicionales."""
        menu_data = [
            # El Kiosko del Vigorón
            {
                "business": businesses["El Kiosko del Vigorón de Doña Vilma"],
                "name": "Vigorón Clásico con Chicharrón de Faja",
                "description": "Yuca fresca con chicharrón crujiente y ensalada de mamey servido en hoja de plátano.",
                "price": Decimal("130.00"),
                "image": "platillos/vigoron-mixto_web.jpg.webp",
                "traditional_food": foods.get("Vigorón Granadino"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["El Kiosko del Vigorón de Doña Vilma"],
                "name": "Vigorón Mixto (Chicharrón y Carne Frita)",
                "description": "Nuestra versión especial combinando chicharrón de faja y trozos tiernos de carne frita.",
                "price": Decimal("170.00"),
                "image": "platillos/vigoron-mixto_web.jpg.webp",
                "traditional_food": foods.get("Vigorón Granadino"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["El Kiosko del Vigorón de Doña Vilma"],
                "name": "Fresco de Grama Helado",
                "description": "Bebida típica refrescante tradicional granadina servida bien fría.",
                "price": Decimal("35.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Quesillos Mi Bohío
            {
                "business": businesses["Quesillos Mi Bohío Nagarote"],
                "name": "Quesillo en Hoja con Doble Crema",
                "description": "Quesillo tradicional suave en hoja con cebolla encurtida y crema pura.",
                "price": Decimal("85.00"),
                "image": "platillos/quesillo.jpg",
                "traditional_food": foods.get("Quesillo de Nagarote"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Quesillos Mi Bohío Nagarote"],
                "name": "Tiste Helado en Jícara",
                "description": "Bebida fría de maíz molido con cacao, canela y raspadura de hielo.",
                "price": Decimal("40.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Fritanga Managüense
            {
                "business": businesses["Fritanga y Asados Managüenses"],
                "name": "Servicio de Carne Asada Completo",
                "description": "Carne de res asada con gallopinto, tajadas fritas y queso asado o frito.",
                "price": Decimal("190.00"),
                "image": "platillos/carne-asada.jpeg",
                "traditional_food": foods.get("Fritanga Managüense"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Fritanga y Asados Managüenses"],
                "name": "Enchilada Especial Nica",
                "description": "Tortilla doblada con arroz y carne picante frita con ensalada de repollo encima.",
                "price": Decimal("65.00"),
                "image": "platillos/enchilada.jpeg",
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # El Rincón de las Rosquillas Somoteñas
            {
                "business": businesses["El Rincón de las Rosquillas Somoteñas"],
                "name": "Bolsa de Rosquillas Tradicionales",
                "description": "Bolsa familiar con 25 rosquillas crocantes elaboradas en horno de leña.",
                "price": Decimal("80.00"),
                "image": "platillos/tortillas.jpg",
                "traditional_food": foods.get("Rosquillas de Somoto"),
                "is_traditional_variant": True,
            },

            # Sabor Caribeño y Rondón
            {
                "business": businesses["Sabor Caribeño y Rondón de Bluefields"],
                "name": "Rondón Mixto de Langosta y Pescado",
                "description": "Caldo espeso con coco, yuca, plátano verde, cola de langosta y filete fresco.",
                "price": Decimal("320.00"),
                "image": "platillos/RONDON.jpg",
                "traditional_food": foods.get("Rondón de Mariscos Caribeño"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Sabor Caribeño y Rondón de Bluefields"],
                "name": "Patí Criollo Especiado",
                "description": "Empanada horneada caribeña con carne molida y toque de chile habanero.",
                "price": Decimal("45.00"),
                "image": "platillos/pati.jpg",
                "traditional_food": foods.get("Patí Bluefileño"),
                "is_traditional_variant": True,
            },
        ]

        for mitem in menu_data:
            item, created = BusinessMenuItem.objects.update_or_create(
                business=mitem["business"],
                name=mitem["name"],
                defaults={
                    "description": mitem["description"],
                    "price": mitem["price"],
                    "image": mitem["image"],
                    "traditional_food": mitem["traditional_food"],
                    "is_traditional_variant": mitem["is_traditional_variant"],
                }
            )
            self.stdout.write(f'  ✓ Menú [{item.business.name}]: {item.name} - C$ {item.price}')

    def create_gastronomic_routes(self, departments, businesses):
        """Crea rutas gastronómicas y asocia los negocios ordenados."""
        routes_data = [
            {
                "name": "Ruta Colonial y del Vigorón",
                "department": departments["Granada"],
                "description": "Recorrido por el Parque Central y calles coloniales saboreando el auténtico vigorón granadino.",
                "businesses": [businesses["El Kiosko del Vigorón de Doña Vilma"]],
            },
            {
                "name": "Ruta de los Quesillos de Occidente",
                "department": departments["León"],
                "description": "Travesía por la carretera hacia León disfrutando el suave quesillo en hoja caliente.",
                "businesses": [businesses["Quesillos Mi Bohío Nagarote"]],
            },
            {
                "name": "Ruta de las Fritangas Capitalinas",
                "department": departments["Managua"],
                "description": "Tarde y noche gastronómica descubriendo el sabor de los mejores asados de Managua.",
                "businesses": [businesses["Fritanga y Asados Managüenses"]],
            },
            {
                "name": "Ruta del Maíz y las Rosquillas de Altura",
                "department": departments["Madriz"],
                "description": "Paseo por Somoto con degustación de rosquillas recién horneadas y café segoviano.",
                "businesses": [businesses["El Rincón de las Rosquillas Somoteñas"]],
            },
            {
                "name": "Ruta Afrocaribeña y del Coco",
                "department": departments["Costa Caribe Sur"],
                "description": "Experiencia costeña al ritmo del palo de mayo con rondón de mariscos y patí.",
                "businesses": [businesses["Sabor Caribeño y Rondón de Bluefields"]],
            },
        ]

        for rdata in routes_data:
            route, created = GastronomicRoute.objects.update_or_create(
                name=rdata["name"],
                defaults={
                    "department": rdata["department"],
                    "description": rdata["description"],
                }
            )
            self.stdout.write(f'  ✓ Ruta: {route.name} ({route.department.name})')

            for order, biz in enumerate(rdata["businesses"], start=1):
                RouteBusiness.objects.update_or_create(
                    route=route,
                    business=biz,
                    defaults={"suggested_order": order}
                )
                self.stdout.write(f'     ↳ Negocio #{order}: {biz.name}')

    def create_qualifications(self, users, businesses):
        """Crea calificaciones y reseñas con fotos de evidencia para probar el cálculo de ratings."""
        qualifications_data = [
            {
                "user": users["turista_juan"],
                "business": businesses["El Kiosko del Vigorón de Doña Vilma"],
                "qualification": 5,
                "comment": "¡El mejor vigorón de toda Nicaragua! El chicharrón súper tostadito y la ensalada bien fresquita.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["Quesillos Mi Bohío Nagarote"],
                "qualification": 5,
                "comment": "Riquísimo quesillo, la crema es súper espesa y el queso suave y caliente.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["carlos_aspira"],
                "business": businesses["Fritanga y Asados Managüenses"],
                "qualification": 4,
                "comment": "Buena porción de carne asada y el gallopinto excelente. Servicio rápido.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["Sabor Caribeño y Rondón de Bluefields"],
                "qualification": 5,
                "comment": "El rondón de langosta es de otro mundo, el sabor a leche de coco natural es inigualable.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
        ]

        for qdata in qualifications_data:
            BusinessQualification.objects.update_or_create(
                user=qdata["user"],
                business=qdata["business"],
                defaults={
                    "qualification": qdata["qualification"],
                    "comment": qdata["comment"],
                    "evidence_image": qdata["evidence_image"],
                }
            )
            self.stdout.write(f'  ✓ Calificación: {qdata["qualification"]}★ por {qdata["user"].username} en {qdata["business"].name}')

    def create_food_collections(self, users, foods):
        """Crea estados de colección para probar la pantalla del Álbum Digital y los stickers."""
        turista = users["turista_juan"]
        collections_data = [
            {"food": foods.get("Vigorón Granadino"), "complete": True},
            {"food": foods.get("Quesillo de Nagarote"), "complete": True},
            {"food": foods.get("Rondón de Mariscos Caribeño"), "complete": True},
            {"food": foods.get("Nacatamal Leones"), "complete": False},
            {"food": foods.get("Rosquillas de Somoto"), "complete": False},
            {"food": foods.get("Indio Viejo Matagalpino"), "complete": False},
        ]

        for cdata in collections_data:
            if cdata["food"]:
                FoodCollection.objects.update_or_create(
                    user=turista,
                    traditional_food=cdata["food"],
                    defaults={"complete": cdata["complete"]}
                )
                estado = "Completado/Desbloqueado" if cdata["complete"] else "Pendiente"
                self.stdout.write(f'  ✓ Colección [{turista.username}]: {cdata["food"].name} -> {estado}')
