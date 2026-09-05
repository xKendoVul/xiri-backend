"""
Command para poblar la base de datos con datos de prueba completos de Nicaragua para Xiri.

Incluye rutas gastronómicas secuenciales de punto A a punto B (ej. Ruta del Quesillo,
Ruta del Vigorón, Ruta de la Fritanga, Ruta de las Rosquillas de Somoto, Ruta del Caribe).

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
from business.models import Business, BusinessMenuItem, Menu, BusinessQualification, RouteBusiness


class Command(BaseCommand):
    help = 'Poblar la base de datos con datos de prueba auténticos de Nicaragua para Xiri con rutas detalladas'

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
            Menu.objects.all().delete()
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

        self.stdout.write('\n2. Creando platillos típicos tradicionales nicaragüenses...')
        foods = self.create_traditional_foods(departments)

        self.stdout.write('\n3. Creando usuarios de prueba (Admin, Dueños de Negocios, Turistas)...')
        users = self.create_users()

        self.stdout.write('\n4. Creando solicitudes de verificación en distintos estados...')
        self.create_verification_requests(users)

        self.stdout.write('\n5. Creando negocios emblemáticos ordenados por rutas geográficas...')
        businesses = self.create_businesses(users)

        self.stdout.write('\n6. Creando platillos en el menú de cada negocio con precios...')
        self.create_menu_items(businesses, foods)

        self.stdout.write('\n7. Creando rutas gastronómicas de punto A a punto B con paradas...')
        self.create_gastronomic_routes(departments, businesses)

        self.stdout.write('\n8. Creando calificaciones y reseñas con fotos de evidencia...')
        self.create_qualifications(users, businesses)

        self.stdout.write('\n9. Creando colección de platillos y progreso del álbum digital...')
        self.create_food_collections(users, foods)

        self.stdout.write(self.style.SUCCESS('\n========================================================================================================'))
        self.stdout.write(self.style.SUCCESS('                        🎉 ¡DATOS DE PRUEBA CARGADOS CON ÉXITO! 🎉'))
        self.stdout.write(self.style.SUCCESS('========================================================================================================'))
        self.stdout.write('  ℹ️  En la app móvil puedes ingresar con tu USUARIO (o CORREO) y tu CONTRASEÑA:\n')
        self.stdout.write('  ┌──────────────────┬─────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐')
        self.stdout.write('  │ ROL              │ USUARIO         │ CONTRASEÑA           │ CORREO               │ PERSONAJE / PROCESO     │')
        self.stdout.write('  ├──────────────────┼─────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤')
        self.stdout.write('  │ 👑 Admin         │ admin           │ admin1234            │ admin@xiri.com       │ Admin / Superusuario    │')
        self.stdout.write('  │ 🏪 Dueño 1       │ don_pedro       │ dueno1234            │ dueno@xiri.com       │ Pedro (Dueño Nagarote)  │')
        self.stdout.write('  │ 🏪 Dueña 2       │ dona_maria      │ duena1234            │ duena@xiri.com       │ María (Dueña Granada)   │')
        self.stdout.write('  │ 🏪 Dueña 3       │ dona_vilma      │ duena1234            │ vilma@xiri.com       │ Vilma (Dueña Nagarote)  │')
        self.stdout.write('  │ 🏪 Dueño 4       │ don_chepe       │ dueno1234            │ chepe@xiri.com       │ Chepe (Dueño Managua)   │')
        self.stdout.write('  │ 🎒 Turista       │ turista_juan    │ turista1234          │ turista@xiri.com     │ Juan (Explorador álbum) │')
        self.stdout.write('  │ 📝 Solicitante   │ carlos_aspira   │ solicitante1234      │ solicitante@xiri.com │ Carlos (Pide ser dueño) │')
        self.stdout.write('  └──────────────────┴─────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘')
        self.stdout.write('  * NOTA: Puedes escribir tanto el USUARIO como el CORREO en el primer campo del login.')
        self.stdout.write(self.style.SUCCESS('========================================================================================================\n'))

    def create_departments(self):
        """Crea los 17 departamentos/regiones de Nicaragua con coordenadas GPS auténticas."""
        departments_data = [
            {"name": "Boaco", "latitude": 12.4729, "longitude": -85.6604,
             "description": "Tierra de dos pisos con encantadores paisajes montañosos, ganadería de altura y rica cuajada."},
            {"name": "Carazo", "latitude": 11.9103, "longitude": -86.2102,
             "description": "Famoso por su clima fresco, festividades de San Sebastián, ajiaco, masa de cazuela y dulces típicos."},
            {"name": "Chinandega", "latitude": 12.6298, "longitude": -87.1318,
             "description": "Cálida tierra volcánica del pacífico norte, rica en mariscos, caña de azúcar y dulces tradicionales."},
            {"name": "Chontales", "latitude": 11.9385, "longitude": -85.1677,
             "description": "Cuna ganadera de Nicaragua, famosa por sus quesillos, carnes asadas y derivados lácteos."},
            {"name": "Estelí", "latitude": 13.0852, "longitude": -86.3533,
             "description": "El diamante de las Segovias, famoso por sus puros de tabaco, murales y desayunos norteños."},
            {"name": "Granada", "latitude": 11.9294, "longitude": -85.9566,
             "description": "La Gran Sultana colonial a orillas del Gran Lago de Nicaragua, cuna indiscutible del vigorón."},
            {"name": "Jinotega", "latitude": 13.1042, "longitude": -86.0024,
             "description": "La ciudad de las brumas, cuna del mejor café especial de altura y deliciosas güirilas de maíz tierno."},
            {"name": "León", "latitude": 12.4382, "longitude": -86.8784,
             "description": "Ciudad universitaria y poética, hogar del nacatamal dominical y de la legendaria ruta de los quesillos."},
            {"name": "Madriz", "latitude": 13.3391, "longitude": -86.5204,
             "description": "Hogar del imponente Cañón de Somoto y las inconfundibles rosquillas somoteñas de horno de leña."},
            {"name": "Managua", "latitude": 12.1150, "longitude": -86.2362,
             "description": "La capital vibrante, famosa por sus fritangas nocturnas, asados al carbón y gran actividad culinaria."},
            {"name": "Masaya", "latitude": 11.9738, "longitude": -86.0964,
             "description": "Capital del folclore nacional y artesanal, célebre por su sabroso vaho, montucas y cajetas de frutas."},
            {"name": "Matagalpa", "latitude": 12.9254, "longitude": -85.9189,
             "description": "La perla del septentrión, tierra del indio viejo tradicional, café aromático y clima templado."},
            {"name": "Nueva Segovia", "latitude": 13.6552, "longitude": -86.1184,
             "description": "Montañas de pinares con rica herencia culinaria a base de maíz criollo, empanadas y atoles."},
            {"name": "Río San Juan", "latitude": 11.4088, "longitude": -84.8380,
             "description": "Santuario tropical y fluvial, hogar del sábalo real, camarones de río y pescados de agua dulce."},
            {"name": "Rivas", "latitude": 11.4373, "longitude": -85.7136,
             "description": "Encrucijada del istmo con playas de surf y rica tradición de mariscos frescos, cacao y dulces."},
            {"name": "Costa Caribe Norte", "latitude": 13.2541, "longitude": -84.8380,
             "description": "Región autónoma de tradición miskita y mayangna, rica en plátanos verdes, luk luk y coco."},
            {"name": "Costa Caribe Sur", "latitude": 12.1389, "longitude": -83.7030,
             "description": "Tierra criolla y afrodescendiente en Bluefields, cuna del rondón marinero, patí picante y pan de coco."},
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
            # León
            {"name": "Quesillo de Nagarote", "department": "León",
             "description": "Tortilla caliente recién salida del comal con queso hilado tierno, cebollita encurtida en vinagre de guineo y abundante crema agria.",
             "cultural_origin": "Platillo típico creado en Nagarote y La Paz Centro a mediados del siglo XX por vendedoras de trenes.",
             "image": "platillos/quesillo.jpg"},
            {"name": "Nacatamal Leones", "department": "León",
             "description": "Masa de maíz criollo perfumada con achiote y manteca, rellena de cerdo marinado, arroz, papa y yerbabuena en hoja de chagüite.",
             "cultural_origin": "Platillo prehispánico perfeccionado en la época colonial, tradición de los domingos nicaragüenses.",
             "image": "platillos/nacatamal.avif"},

            # Granada
            {"name": "Vigorón Granadino", "department": "Granada",
             "description": "Yuca cocida suave con chicharrón crocante de faja y ensalada de repollo con mamey y tomate en hoja de plátano.",
             "cultural_origin": "Nacido en 1914 en Granada por la famosa 'Loca Ramona', símbolo gastronómico por excelencia.",
             "image": "platillos/vigoron-mixto_web.jpg.webp"},

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

            # Madriz
            {"name": "Rosquillas de Somoto", "department": "Madriz",
             "description": "Horneadas crocantes de masa de maíz selecto con cuajada fresca y queso seco de la más alta calidad.",
             "cultural_origin": "Reconocidas nacional e internacionalmente como el mayor orgullo culinario de Somoto.",
             "image": "platillos/tortillas.jpg"},

            # Matagalpa
            {"name": "Indio Viejo Matagalpino", "department": "Matagalpa",
             "description": "Guiso de masa de maíz condimentado con yerbabuena, achiote, cebolla y carne de res deshilachada en naranja agria.",
             "cultural_origin": "Plato prehispánico legendario de las tribus indígenas del norte de Nicaragua.",
             "image": "platillos/indio.jpeg"},

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

            # Chinandega
            {"name": "Pescado Frito Tipitapa", "department": "Chinandega",
             "description": "Pescado entero frito crocante bañado en una abundante salsa criolla de tomates frescos, cebolla y chiltoma.",
             "cultural_origin": "Tradición costera del pacífico nicaragüense preferida por locales y turistas.",
             "image": "platillos/images.jpeg"},
            {"name": "Sopa de Queso Cuaresmeña", "department": "Chinandega",
             "description": "Caldo enriquecido con masa y tortas fritas de queso seco, aromatizado con hierbabuena y cebolla.",
             "cultural_origin": "Platillo esencial de la Semana Santa y Cuaresma nicaragüense.",
             "image": "platillos/sopa-queso.jpg"},

            # Costa Caribe Norte
            {"name": "Guabul Misquito", "department": "Costa Caribe Norte",
             "description": "Bebida tradicional a base de plátano verde madurado cocido, leche de vaca y leche de coco.",
             "cultural_origin": "Bebida típica cotidiana de la comunidad indígena miskita en Bilwi.",
             "image": "platillos/guabul.webp"},

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
                "username": "dona_vilma",
                "email": "vilma@xiri.com",
                "password": "duena1234",
                "first_name": "Vilma",
                "last_name": "Ruiz",
                "rol": "owner",
                "contact_number": "+50585551111",
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "don_chepe",
                "email": "chepe@xiri.com",
                "password": "dueno1234",
                "first_name": "José",
                "last_name": "Torres",
                "rol": "owner",
                "contact_number": "+50584442222",
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
            self.stdout.write(f'  ✓ Usuario: {user.username:<14} | Contraseña: {udata["password"]:<15} | Rol: {user.rol:<6} | Correo: {user.email}')

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
        """Crea negocios auténticos con coordenadas GPS precisas organizadas a lo largo de rutas viales."""
        businesses_data = [
            # ==========================================
            # RUTA DEL QUESILLO (Carretera Nueva a León)
            # ==========================================
            {
                "name": "Quesillos El Güiligüiste",
                "contact_number": "+50588881111",
                "address": "Km 40 Carretera Nueva a León, Nagarote",
                "latitude": Decimal("12.264500"),
                "longitude": Decimal("-86.611500"),
                "owner": users["dona_vilma"],
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
                "name": "Quesillos Acadia La Paz Centro",
                "contact_number": "+50588882222",
                "address": "Km 56 Carretera Nueva a León, La Paz Centro",
                "latitude": Decimal("12.339500"),
                "longitude": Decimal("-86.674500"),
                "owner": users["don_chepe"],
            },
            {
                "name": "Quesillos y Dulces Doña Tania",
                "contact_number": "+50588883333",
                "address": "Km 58 Carretera Nueva a León, La Paz Centro",
                "latitude": Decimal("12.344000"),
                "longitude": Decimal("-86.679000"),
                "owner": users["dona_maria"],
            },

            # ==========================================
            # RUTA COLONIAL DEL VIGORÓN (Granada)
            # ==========================================
            {
                "name": "El Kiosko del Vigorón de Doña Vilma",
                "contact_number": "+50589996666",
                "address": "Costado Sur del Parque Central, Granada",
                "latitude": Decimal("11.929800"),
                "longitude": Decimal("-85.956000"),
                "owner": users["dona_vilma"],
            },
            {
                "name": "Vigorón La Abuela de La Calzada",
                "contact_number": "+50589991111",
                "address": "Calle La Calzada, frente a Hotel Darío, Granada",
                "latitude": Decimal("11.930500"),
                "longitude": Decimal("-85.953500"),
                "owner": users["dona_maria"],
            },
            {
                "name": "Rincón Criollo del Malecón de Granada",
                "contact_number": "+50589992222",
                "address": "Paseo del Malecón, frente a Puerto Asese, Granada",
                "latitude": Decimal("11.932000"),
                "longitude": Decimal("-85.948000"),
                "owner": users["don_chepe"],
            },

            # ==========================================
            # RUTA DE LA FRITANGA MANAGÜENSE (Managua)
            # ==========================================
            {
                "name": "Fritanga y Asados Managüenses",
                "contact_number": "+50588887777",
                "address": "Rotonda Bello Horizonte, 1 c. al sur, Managua",
                "latitude": Decimal("12.146500"),
                "longitude": Decimal("-86.230100"),
                "owner": users["don_pedro"],
            },
            {
                "name": "Asados y Fritanga El Bohemo",
                "contact_number": "+50588884444",
                "address": "Colonia Centroamérica, costado este del parque, Managua",
                "latitude": Decimal("12.112000"),
                "longitude": Decimal("-86.248000"),
                "owner": users["don_chepe"],
            },
            {
                "name": "Fritanga Doña Chepita de Linda Vista",
                "contact_number": "+50588885555",
                "address": "Semáforos de Linda Vista, 2 c. al norte, Managua",
                "latitude": Decimal("12.155000"),
                "longitude": Decimal("-86.301000"),
                "owner": users["dona_vilma"],
            },

            # ==========================================
            # RUTA DEL CAFÉ Y ROSQUILLAS (Madriz / Estelí)
            # ==========================================
            {
                "name": "Café y Desayuno Campesino El Diamante",
                "contact_number": "+50587771111",
                "address": "Salida Norte de Estelí, Km 152 Panamericana",
                "latitude": Decimal("13.098000"),
                "longitude": Decimal("-86.357000"),
                "owner": users["don_pedro"],
            },
            {
                "name": "Taller Artesanal de Rosquillas Doña Vílchez",
                "contact_number": "+50587772222",
                "address": "Entrada a Somoto, Km 218 Panamericana Norte",
                "latitude": Decimal("13.479000"),
                "longitude": Decimal("-86.581000"),
                "owner": users["dona_vilma"],
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
                "name": "Comedor Campestre El Cañón de Somoto",
                "contact_number": "+50587773333",
                "address": "Comunidad Sonís, Entrada al Cañón de Somoto",
                "latitude": Decimal("13.468000"),
                "longitude": Decimal("-86.645000"),
                "owner": users["don_chepe"],
            },

            # ==========================================
            # RUTA AFROCARIBEÑA Y DEL COCO (Bluefields)
            # ==========================================
            {
                "name": "Sabor Caribeño y Rondón de Bluefields",
                "contact_number": "+50588887777",
                "address": "Barrio Punta Fría, frente al muelle municipal, Bluefields",
                "latitude": Decimal("12.013500"),
                "longitude": Decimal("-83.763500"),
                "owner": users["don_pedro"],
            },
            {
                "name": "Miss Becca's Kitchen & Patí House",
                "contact_number": "+50588886666",
                "address": "Barrio Cotton Tree, calle principal, Bluefields",
                "latitude": Decimal("12.011000"),
                "longitude": Decimal("-83.765000"),
                "owner": users["dona_maria"],
            },
            {
                "name": "El Oasis Costeño Seafood",
                "contact_number": "+50588888888",
                "address": "Barrio Beholden, frente a la bahía, Bluefields",
                "latitude": Decimal("12.008000"),
                "longitude": Decimal("-83.768000"),
                "owner": users["don_chepe"],
            },

            # ==========================================
            # RUTA DE LAS BRUMAS Y GÜIRILAS (Matagalpa - Jinotega)
            # ==========================================
            {
                "name": "Comedor El Indio Viejo Matagalpino",
                "contact_number": "+50586661111",
                "address": "Paseo Juan Pablo II, Matagalpa",
                "latitude": Decimal("12.924000"),
                "longitude": Decimal("-85.919000"),
                "owner": users["don_pedro"],
            },
            {
                "name": "Güirilas con Cuajada Las Brumas",
                "contact_number": "+50586662222",
                "address": "Km 140 Carretera Matagalpa a Jinotega",
                "latitude": Decimal("13.015000"),
                "longitude": Decimal("-85.965000"),
                "owner": users["dona_vilma"],
            },
            {
                "name": "El Mirador de Jinotega Café & Tradición",
                "contact_number": "+50586663333",
                "address": "Entrada sur a Jinotega, Mirador La Peña",
                "latitude": Decimal("13.098000"),
                "longitude": Decimal("-86.002000"),
                "owner": users["dona_maria"],
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
            # Quesillos El Güiligüiste
            {
                "business": businesses["Quesillos El Güiligüiste"],
                "name": "Quesillo Tradicional en Hoja",
                "description": "El clásico quesillo nagaroteño en hoja de chagüite con cebolla encurtida artesanal y crema agria fresca.",
                "price": Decimal("85.00"),
                "image": "platillos/quesillo.jpg",
                "traditional_food": foods.get("Quesillo de Nagarote"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Quesillos El Güiligüiste"],
                "name": "Tiste Helado en Jícara Artesanal",
                "description": "Maíz tostado molido finamente con cacao y especias, servido bien frío en jícara tradicional.",
                "price": Decimal("35.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Quesillos Mi Bohío
            {
                "business": businesses["Quesillos Mi Bohío Nagarote"],
                "name": "Quesillo Doble Especial con Crema",
                "description": "Porción generosa de queso hilado fresco con doble capa de crema agria espesa.",
                "price": Decimal("95.00"),
                "image": "platillos/quesillo.jpg",
                "traditional_food": foods.get("Quesillo de Nagarote"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Quesillos Mi Bohío Nagarote"],
                "name": "Fresco de Cacao con Leche",
                "description": "Cacao nicaragüense auténtico molido con leche entera y canela.",
                "price": Decimal("40.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Quesillos Acadia
            {
                "business": businesses["Quesillos Acadia La Paz Centro"],
                "name": "Quesillo de Comal La Paz Centro",
                "description": "Tortilla de comal recién volteada con quesillo hilado caliente y vinagreta de cebollita picada.",
                "price": Decimal("85.00"),
                "image": "platillos/quesillo.jpg",
                "traditional_food": foods.get("Quesillo de Nagarote"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Quesillos Acadia La Paz Centro"],
                "name": "Cosa de Horno Pacence",
                "description": "Pan dulce tradicional de maíz con queso horneado en comal de barro.",
                "price": Decimal("45.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Quesillos Doña Tania
            {
                "business": businesses["Quesillos y Dulces Doña Tania"],
                "name": "Quesillo en Trenza Casero",
                "description": "Queso tierno en trenza artesanal bañado con crema dulce o ácida a su gusto.",
                "price": Decimal("90.00"),
                "image": "platillos/quesillo.jpg",
                "traditional_food": foods.get("Quesillo de Nagarote"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Quesillos y Dulces Doña Tania"],
                "name": "Chicha de Maíz Helada",
                "description": "Bebida fermentada dulce de maíz rosado con esencia de vainilla y frambuesa.",
                "price": Decimal("30.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

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
                "name": "Fresco de Grama Helado",
                "description": "Bebida típica refrescante tradicional granadina servida bien fría.",
                "price": Decimal("35.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Vigorón La Abuela
            {
                "business": businesses["Vigorón La Abuela de La Calzada"],
                "name": "Vigorón Mixto de Chicharrón y Carne",
                "description": "Nuestra versión especial combinando chicharrón de faja y trozos tiernos de carne frita.",
                "price": Decimal("170.00"),
                "image": "platillos/vigoron-mixto_web.jpg.webp",
                "traditional_food": foods.get("Vigorón Granadino"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Vigorón La Abuela de La Calzada"],
                "name": "Guapote sin Espinas en Salsa Criolla",
                "description": "Pescado del Gran Lago frito y cubierto con cebolla y tomate salteados.",
                "price": Decimal("280.00"),
                "image": "platillos/images.jpeg",
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Rincón Criollo del Malecón
            {
                "business": businesses["Rincón Criollo del Malecón de Granada"],
                "name": "Vigorón Criollo Especial del Muelle",
                "description": "Vigorón completo acompañado de chicharrón con carne y chilitos congo al gusto.",
                "price": Decimal("150.00"),
                "image": "platillos/vigoron-mixto_web.jpg.webp",
                "traditional_food": foods.get("Vigorón Granadino"),
                "is_traditional_variant": True,
            },

            # Fritanga Managüense
            {
                "business": businesses["Fritanga y Asados Managüenses"],
                "name": "Servicio de Carne Asada Completo",
                "description": "Carne de res asada con gallopinto, tajadas verdes crocantes y queso frito nica.",
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

            # Asados El Bohemo
            {
                "business": businesses["Asados y Fritanga El Bohemo"],
                "name": "Servicio de Cerdo Asado al Carbón",
                "description": "Lomo de cerdo marinado con naranja agria, gallopinto montañero y tajadas fritas.",
                "price": Decimal("180.00"),
                "image": "platillos/carne-asada.jpeg",
                "traditional_food": foods.get("Fritanga Managüense"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Asados y Fritanga El Bohemo"],
                "name": "Maduro con Queso Frito",
                "description": "Plátano maduro asado dulce con trozo generoso de queso criollo frito.",
                "price": Decimal("60.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Fritanga Doña Chepita
            {
                "business": businesses["Fritanga Doña Chepita de Linda Vista"],
                "name": "Servicio de Pollo Asado Fritanguero",
                "description": "Cuarto de pollo asado con chimichurri nica, gallopinto y tajadas verdes con ensalada.",
                "price": Decimal("170.00"),
                "image": "platillos/pollo-carbon.jpeg",
                "traditional_food": foods.get("Pollo Asado al Carbón"),
                "is_traditional_variant": True,
            },

            # Café El Diamante
            {
                "business": businesses["Café y Desayuno Campesino El Diamante"],
                "name": "Desayuno Tres Golpes Norteño",
                "description": "Huevos fritos, gallopinto norteño, tajadas y queso frito con tortilla de maíz recién hecha.",
                "price": Decimal("140.00"),
                "image": "platillos/tres-g.jpg",
                "traditional_food": foods.get("Desayuno Tres Golpes Norteño"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Café y Desayuno Campesino El Diamante"],
                "name": "Café Especial de Altura",
                "description": "Café arábica de estricta altura cultivado en las montañas segovianas.",
                "price": Decimal("35.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Rosquillas Doña Vílchez
            {
                "business": businesses["Taller Artesanal de Rosquillas Doña Vílchez"],
                "name": "Bolsa de Rosquillas Recién Horneadas",
                "description": "Rosquillas tradicionales de maíz y cuajada cocidas a fuego lento en horno de barro.",
                "price": Decimal("75.00"),
                "image": "platillos/tortillas.jpg",
                "traditional_food": foods.get("Rosquillas de Somoto"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Taller Artesanal de Rosquillas Doña Vílchez"],
                "name": "Hojaldras Dulces de Somoto",
                "description": "Hojaldras crujientes elaboradas con maíz dulce y panela.",
                "price": Decimal("60.00"),
                "image": "platillos/tortillas.jpg",
                "traditional_food": foods.get("Rosquillas de Somoto"),
                "is_traditional_variant": True,
            },

            # El Rincón de las Rosquillas
            {
                "business": businesses["El Rincón de las Rosquillas Somoteñas"],
                "name": "Bolsa Familiar de Rosquillas Tradicionales",
                "description": "Bolsa familiar con 25 rosquillas crocantes elaboradas con la receta centenaria.",
                "price": Decimal("80.00"),
                "image": "platillos/tortillas.jpg",
                "traditional_food": foods.get("Rosquillas de Somoto"),
                "is_traditional_variant": True,
            },

            # Comedor El Cañón
            {
                "business": businesses["Comedor Campestre El Cañón de Somoto"],
                "name": "Plato Típico Somoteño con Cuajada",
                "description": "Carne cecina con gallopinto, cuajada fresca de hacienda, tortillas y café negro.",
                "price": Decimal("160.00"),
                "image": "platillos/carne-asada.jpeg",
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # Sabor Caribeño Bluefields
            {
                "business": businesses["Sabor Caribeño y Rondón de Bluefields"],
                "name": "Rondón Mixto de Langosta y Pescado",
                "description": "Caldo espeso con coco, yuca, plátano verde, cola de langosta y filete fresco.",
                "price": Decimal("320.00"),
                "image": "platillos/RONDON.jpg",
                "traditional_food": foods.get("Rondón de Mariscos Caribeño"),
                "is_traditional_variant": True,
            },

            # Miss Becca's
            {
                "business": businesses["Miss Becca's Kitchen & Patí House"],
                "name": "Patí Bluefileño Especiado (2 unidades)",
                "description": "Empanadas doradas con relleno de carne molida al estilo caribeño picante.",
                "price": Decimal("80.00"),
                "image": "platillos/pati.jpg",
                "traditional_food": foods.get("Patí Bluefileño"),
                "is_traditional_variant": True,
            },
            {
                "business": businesses["Miss Becca's Kitchen & Patí House"],
                "name": "Pan de Coco Horneado",
                "description": "Bollo esponjoso amasado con leche de coco pura recién extraída.",
                "price": Decimal("35.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # El Oasis Costeño
            {
                "business": businesses["El Oasis Costeño Seafood"],
                "name": "Rondón Tradicional de Pescado Entero",
                "description": "Receta ancestral con leche de coco, malanga, quequisque y pescado pargo rojo.",
                "price": Decimal("280.00"),
                "image": "platillos/RONDON.jpg",
                "traditional_food": foods.get("Rondón de Mariscos Caribeño"),
                "is_traditional_variant": True,
            },

            # Comedor El Indio Viejo
            {
                "business": businesses["Comedor El Indio Viejo Matagalpino"],
                "name": "Cazuela de Indio Viejo Tradicional",
                "description": "Masa de maíz criollo espesada con caldo de res, hierbabuena y naranja agria.",
                "price": Decimal("150.00"),
                "image": "platillos/indio.jpeg",
                "traditional_food": foods.get("Indio Viejo Matagalpino"),
                "is_traditional_variant": True,
            },

            # Güirilas Las Brumas
            {
                "business": businesses["Güirilas con Cuajada Las Brumas"],
                "name": "Güirila Caliente con Cuajada Fresca",
                "description": "Tortilla dulce de maíz tierno (choclo) asada en comal con una rueda de cuajada campesina y crema.",
                "price": Decimal("95.00"),
                "image": "platillos/tortillas.jpg",
                "traditional_food": None,
                "is_traditional_variant": False,
            },
            {
                "business": businesses["Güirilas con Cuajada Las Brumas"],
                "name": "Atol de Maíz Tierno Dulce",
                "description": "Bebida caliente y cremosa de maíz tierno con canela en raja y leche.",
                "price": Decimal("45.00"),
                "image": None,
                "traditional_food": None,
                "is_traditional_variant": False,
            },

            # El Mirador de Jinotega
            {
                "business": businesses["El Mirador de Jinotega Café & Tradición"],
                "name": "Montucas de Cerdo Norteñas",
                "description": "Tamalitos norteños de maíz tierno rellenos de trocitos de cerdo sazonado.",
                "price": Decimal("75.00"),
                "image": "platillos/montuca.jpeg",
                "traditional_food": foods.get("Montucas de Maíz"),
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
            Menu.objects.update_or_create(
                business=item.business,
                menu_item=item,
                defaults={"price": item.price}
            )
            self.stdout.write(f'  ✓ Menú [{item.business.name}]: {item.name} - C$ {item.price}')

    def create_gastronomic_routes(self, departments, businesses):
        """Crea rutas gastronómicas secuenciales de punto A a punto B con paradas ordenadas."""
        routes_data = [
            # 1. RUTA DEL QUESILLO
            {
                "name": "Ruta del Quesillo: De Managua a León por Carretera Nueva",
                "department": departments["León"],
                "description": "La travesía quesillera más icónica de Nicaragua. Recorre la Carretera Nueva a León descubriendo cómo varía el toque de la cebollita, la crema y el queso de Nagarote a La Paz Centro.",
                "businesses": [
                    businesses["Quesillos El Güiligüiste"],
                    businesses["Quesillos Mi Bohío Nagarote"],
                    businesses["Quesillos Acadia La Paz Centro"],
                    businesses["Quesillos y Dulces Doña Tania"],
                ],
            },

            # 2. RUTA DEL VIGORÓN
            {
                "name": "Ruta Colonial del Vigorón: El Sendero Granadino",
                "department": departments["Granada"],
                "description": "Camino peatonal y colonial desde el Parque Central hasta el Muelle del Gran Lago. Degusta las diferentes recetas de vigorón con chicharrón de faja y ensalada fresca.",
                "businesses": [
                    businesses["El Kiosko del Vigorón de Doña Vilma"],
                    businesses["Vigorón La Abuela de La Calzada"],
                    businesses["Rincón Criollo del Malecón de Granada"],
                ],
            },

            # 3. RUTA DE LA FRITANGA
            {
                "name": "Ruta Nocturna de la Fritanga Managüense",
                "department": departments["Managua"],
                "description": "Un tour nocturno por los barrios de la capital degustando la auténtica carne asada con tajadas, queso frito y gallopinto al carbón.",
                "businesses": [
                    businesses["Fritanga y Asados Managüenses"],
                    businesses["Asados y Fritanga El Bohemo"],
                    businesses["Fritanga Doña Chepita de Linda Vista"],
                ],
            },

            # 4. RUTA DE LAS ROSQUILLAS Y CAFÉ
            {
                "name": "Ruta Panamericana del Café y las Rosquillas Somoteñas",
                "department": departments["Madriz"],
                "description": "Viaje norteño por la Carretera Panamericana desde los cafetales de Estelí hasta los legendarios hornos de barro de Somoto y el Cañón.",
                "businesses": [
                    businesses["Café y Desayuno Campesino El Diamante"],
                    businesses["Taller Artesanal de Rosquillas Doña Vílchez"],
                    businesses["El Rincón de las Rosquillas Somoteñas"],
                    businesses["Comedor Campestre El Cañón de Somoto"],
                ],
            },

            # 5. RUTA DEL CARIBE
            {
                "name": "Ruta Afrocaribeña del Rondón y el Coco en Bluefields",
                "department": departments["Costa Caribe Sur"],
                "description": "Inmersión cultural por los barrios costeros de Bluefields con paradas obligatorias para probar rondón de langosta y pescado, patí especiado y pan de coco.",
                "businesses": [
                    businesses["Sabor Caribeño y Rondón de Bluefields"],
                    businesses["Miss Becca's Kitchen & Patí House"],
                    businesses["El Oasis Costeño Seafood"],
                ],
            },

            # 6. RUTA DE LAS GÜIRILAS Y MAÍZ
            {
                "name": "Ruta de las Brumas, Güirilas y el Maíz Norteño",
                "department": departments["Matagalpa"],
                "description": "Travesía panorámica entre las montañas de Matagalpa y Jinotega deleitándote con güirilas calientes, cuajada fresca y atoles de maíz tierno.",
                "businesses": [
                    businesses["Comedor El Indio Viejo Matagalpino"],
                    businesses["Güirilas con Cuajada Las Brumas"],
                    businesses["El Mirador de Jinotega Café & Tradición"],
                ],
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
            self.stdout.write(f'\n  ✓ Ruta: {route.name} ({route.department.name})')

            for order, biz in enumerate(rdata["businesses"], start=1):
                RouteBusiness.objects.update_or_create(
                    route=route,
                    business=biz,
                    defaults={"suggested_order": order}
                )
                self.stdout.write(f'     ↳ Parada #{order}: {biz.name} ({biz.address})')

    def create_qualifications(self, users, businesses):
        """Crea calificaciones y reseñas con fotos de evidencia para probar el cálculo de ratings."""
        qualifications_data = [
            {
                "user": users["turista_juan"],
                "business": businesses["Quesillos El Güiligüiste"],
                "qualification": 5,
                "comment": "¡Parada obligatoria de toda la vida! El quesillo en hoja con cebollita es inigualable.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["Quesillos Mi Bohío Nagarote"],
                "qualification": 5,
                "comment": "Riquísimo quesillo, la crema es súper espesa y el queso suave y calientito.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["carlos_aspira"],
                "business": businesses["Quesillos Acadia La Paz Centro"],
                "qualification": 4,
                "comment": "Buen quesillo al estilo La Paz Centro, tortilla recién hecha y excelente tiste.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["El Kiosko del Vigorón de Doña Vilma"],
                "qualification": 5,
                "comment": "¡El mejor vigorón de toda Nicaragua! El chicharrón súper tostadito y la ensalada bien fresquita.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["carlos_aspira"],
                "business": businesses["Vigorón La Abuela de La Calzada"],
                "qualification": 5,
                "comment": "Excelente ambiente en La Calzada y el vigorón mixto tiene un sabor espectacular.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["Fritanga y Asados Managüenses"],
                "qualification": 4,
                "comment": "Buena porción de carne asada y el gallopinto excelente. Servicio rápido y alegre.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["El Rincón de las Rosquillas Somoteñas"],
                "qualification": 5,
                "comment": "Las rosquillas de Somoto son oro puro. Llegaron calientitas con un café delicioso.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["carlos_aspira"],
                "business": businesses["Taller Artesanal de Rosquillas Doña Vílchez"],
                "qualification": 5,
                "comment": "Ver cómo las hornean a leña le da un sabor único. Compré 4 bolsas para llevar.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["Sabor Caribeño y Rondón de Bluefields"],
                "qualification": 5,
                "comment": "El rondón de langosta es de otro mundo, el sabor a leche de coco natural es inigualable.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["carlos_aspira"],
                "business": businesses["Miss Becca's Kitchen & Patí House"],
                "qualification": 5,
                "comment": "El mejor patí picante de Bluefields. La masa hojaldrada es crujiente y deliciosa.",
                "evidence_image": "reviews/evidence/evidence_sample.jpg",
            },
            {
                "user": users["turista_juan"],
                "business": businesses["Güirilas con Cuajada Las Brumas"],
                "qualification": 5,
                "comment": "Comer una güirila calientita con cuajada viendo la neblina de Matagalpa a Jinotega no tiene precio.",
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
            {"food": foods.get("Patí Bluefileño"), "complete": True},
            {"food": foods.get("Rosquillas de Somoto"), "complete": True},
            {"food": foods.get("Fritanga Managüense"), "complete": True},
            {"food": foods.get("Nacatamal Leones"), "complete": False},
            {"food": foods.get("Indio Viejo Matagalpino"), "complete": False},
            {"food": foods.get("Desayuno Tres Golpes Norteño"), "complete": False},
            {"food": foods.get("Vaho Tradicional"), "complete": False},
        ]

        for cdata in collections_data:
            if cdata["food"]:
                FoodCollection.objects.update_or_create(
                    user=turista,
                    traditional_food=cdata["food"],
                    defaults={"complete": cdata["complete"]}
                )
                estado = "Completado/Desbloqueado ⭐" if cdata["complete"] else "Pendiente"
                self.stdout.write(f'  ✓ Colección [{turista.username}]: {cdata["food"].name} -> {estado}')
