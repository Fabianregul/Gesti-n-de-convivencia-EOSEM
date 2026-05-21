from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.http import HttpResponse
from .models import Estudiante, Reporte

# ReportLab para el PDF, asegúrarnos de tenerlo instalado: pip install reportlab
import os
from reportlab.pdfgen import canvas
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle

# --- AUTENTICACIÓN ---

def view_login(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Usuario o contraseña incorrectos")
    return render(request, 'login.html')

def view_logout(request):
    logout(request)
    return redirect('login')

# --- GESTIÓN DE ESTUDIANTES ---

@login_required
def dashboard(request):
    query = request.GET.get('busqueda')
    if query:
        estudiantes = Estudiante.objects.filter(nombre__icontains=query) | \
                     Estudiante.objects.filter(codigo__icontains=query) | \
                     Estudiante.objects.filter(grado__icontains=query)
    else:
        estudiantes = Estudiante.objects.all()
    return render(request, 'dashboard.html', {'estudiantes': estudiantes})

@login_required
def guardar_estudiante(request):
    if request.method == 'POST':
        Estudiante.objects.create(
            codigo=request.POST.get('cod'),
            nombre=request.POST.get('nom'),
            grado=request.POST.get('gra'),
            acudiente=request.POST.get('acu'),
            celular=request.POST.get('cel')
        )
    return redirect('dashboard')

@login_required
def eliminar_estudiante(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    estudiante.delete()
    return redirect('dashboard')

# --- REPORTES ---

@login_required
def guardar_reporte(request):
    if request.method == 'POST':
        est_id = request.POST.get('estudiante_id')
        estudiante = get_object_or_404(Estudiante, id=est_id)
        Reporte.objects.create(
            estudiante=estudiante,
            tipo=request.POST.get('tipo'),
            descripcion=request.POST.get('descripcion'),
            fecha=request.POST.get('fecha')
        )
    return redirect('dashboard')

@login_required
def editar_estudiante(request, id):
    estudiante = get_object_or_404(Estudiante, id=id)
    if request.method == 'POST':
        estudiante.codigo = request.POST.get('cod')
        estudiante.nombre = request.POST.get('nom')
        estudiante.grado = request.POST.get('gra')
        estudiante.acudiente = request.POST.get('acu')
        estudiante.celular = request.POST.get('cel')
        estudiante.save()
        messages.success(request, "Datos del estudiante actualizados.")
    return redirect('dashboard')

@login_required
def eliminar_estudiante(request, id):
    if request.method == 'POST':
        estudiante = get_object_or_404(Estudiante, id=id)
        password_confirm = request.POST.get('password_confirm')
        
        # Validar contraseña del usuario logueado
        if check_password(password_confirm, request.user.password):
            estudiante.delete()
            messages.success(request, "Estudiante eliminado correctamente.")
        else:
            messages.error(request, "Contraseña incorrecta. No se pudo eliminar.")
            
    return redirect('dashboard')

@login_required
def ver_reportes(request):
    query = request.GET.get('q')
    estudiante = None
    reportes = []
    
    if query:
        estudiante = Estudiante.objects.filter(codigo=query).first() or \
                     Estudiante.objects.filter(nombre__icontains=query).first()
        
        if estudiante:
            reportes = estudiante.reportes.all().order_by('-fecha')

    return render(request, 'reportes.html', {
        'estudiante': estudiante,
        'reportes': reportes
    })

# --- NUEVA VISTA: DESCARGAR PDF ---
@login_required
def descargar_pdf(request):
    if request.method == 'POST':
        codigo = request.POST.get('cod_pdf')
        nombre = request.POST.get('nom_pdf')

        # Buscamos al estudiante
        estudiante = Estudiante.objects.filter(codigo=codigo, nombre__icontains=nombre).first()

        if estudiante:
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Reporte_{estudiante.codigo}.pdf"'

            p = canvas.Canvas(response, pagesize=letter)
            width, height = letter
            
            # --- 1. CONFIGURACIÓN DE COLORES Y RUTAS ---
            azul_institucional = colors.HexColor('#003366')
            gris_suave = colors.HexColor('#F2F2F2')
            ruta_logo = os.path.join(settings.BASE_DIR, 'dashboard/static/img/logotipo.png')

            # --- 2. LOGO CENTRADO ---
            if os.path.exists(ruta_logo):
                # drawImage(ruta, x, y, width, height) -> Centrado: (AnchoPagina/2 - AnchoImagen/2)
                p.drawImage(ruta_logo, (width/2) - 40, height - 100, width=80, height=80, preserveAspectRatio=True, mask='auto')

            # --- 3. ENCABEZADO INSTITUCIONAL ---
            p.setFont("Helvetica-Bold", 16)
            p.setFillColor(azul_institucional)
            p.drawCentredString(width/2, height - 120, "ESCUELA OBRA SOCIAL EL MILAGRO")
            
            p.setFont("Helvetica", 10)
            p.setFillColor(colors.black)
            p.drawCentredString(width/2, height - 135, "SISTEMA DE GESTIÓN DE CONVIVENCIA ESCOLAR (EOSEM)")
            p.drawCentredString(width/2, height - 150, "REGISTRO OFICIAL DE NOVEDADES Y OBSERVACIONES")

            p.setStrokeColor(azul_institucional)
            p.setLineWidth(2)
            p.line(50, height - 160, width - 50, height - 160)

            # --- 4. INFORMACIÓN DEL ESTUDIANTE (Cuadro de datos) ---
            p.setFillColor(gris_suave)
            p.rect(50, height - 230, width - 100, 60, fill=1, stroke=0)
            
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 11)
            p.drawString(60, height - 185, f"ESTUDIANTE: {estudiante.nombre.upper()}")
            p.setFont("Helvetica", 10)
            p.drawString(60, height - 205, f"CÓDIGO: {estudiante.codigo}")
            p.drawString(250, height - 205, f"GRADO: {estudiante.grado}")
            p.drawString(60, height - 220, f"ACUDIENTE: {estudiante.acudiente or 'No registrado'}")
            p.drawString(250, height - 220, f"TELÉFONO: {estudiante.celular or 'No registrado'}")

            # --- 5. RESUMEN DISCIPLINARIO (Estilo de medallas/contadores) ---
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, height - 255, "RESUMEN DISCIPLINARIO")
            
            # Dibujar pequeños cuadros para los totales
            tipos = [
                (f"FTL: {estudiante.total_ftl}", colors.green),
                (f"FTG: {estudiante.total_ftg}", colors.orange),
                (f"FTGR: {estudiante.total_ftgr}", colors.red),
                (f"INAS: {estudiante.total_inas}", colors.blue)
            ]
            
            x_offset = 50
            for texto, color_base in tipos:
                p.setFillColor(color_base)
                p.rect(x_offset, height - 285, 85, 20, fill=1, stroke=0)
                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 9)
                p.drawCentredString(x_offset + 42, height - 278, texto)
                x_offset += 100

            # --- 6. TABLA DE DETALLES (Platypus para mejor estilo) ---
            p.setFillColor(azul_institucional)
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, height - 315, "DETALLE DE OBSERVACIONES Y FALTAS")

            data = [['FECHA', 'TIPO DE NOVEDAD', 'OBSERVACIÓN / DESCRIPCIÓN']]
            reportes = estudiante.reportes.all().order_by('-fecha')
            
            for r in reportes:
                fecha = r.fecha.strftime('%d/%m/%Y')
                tipo = r.get_tipo_display()
                # Cortamos la descripción si es muy larga para que quepa en la fila
                desc = (r.descripcion[:75] + '..') if len(r.descripcion) > 75 else r.descripcion
                data.append([fecha, tipo, desc])

            # Crear la tabla
            tabla = Table(data, colWidths=[80, 120, 300])
            
            # Estilo de la tabla
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), azul_institucional),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, gris_suave])
            ])
            tabla.setStyle(style)

            # Dibujar la tabla en el canvas
            tabla.wrapOn(p, width, height)
            tabla.drawOn(p, 50, height - 340 - (len(data) * 22))

            # --- 7. PIE DE PÁGINA Y FIRMAS ---
            # Posicionamos las firmas al final de la hoja de forma fija
            p.setDash(1, 2) # Línea punteada
            p.line(50, 100, 220, 100)
            p.line(350, 100, 520, 100)
            p.setDash() # Volver a línea sólida
            
            p.setFont("Helvetica", 9)
            p.drawCentredString(135, 85, "FIRMA DEL ESTUDIANTE")
            p.drawCentredString(135, 75, f"C.I. / Código: {estudiante.codigo}")
            
            p.drawCentredString(435, 85, "COORDINACIÓN / DOCENTE")
            p.drawCentredString(435, 75, "Escuela Obra Social El Milagro")

            # Fecha de expedición
            import datetime
            hoy = datetime.date.today().strftime('%d de %B de %Y')
            p.setFont("Helvetica-Oblique", 8)
            p.drawRightString(width - 50, 30, f"Reporte generado el: {hoy}")

            p.showPage()
            p.save()
            return response
        
        else:
            messages.error(request, "Datos incorrectos. Verifica el código y nombre.")
            return redirect('dashboard')
            
    return redirect('dashboard')