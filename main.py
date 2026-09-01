import flet as ft
import flet.canvas as cv
import math

def parse_num(val: str, default: float = 0.0) -> float:
    """Convierte texto a float soportando comas y puntos decimales."""
    try:
        if not val or not str(val).strip():
            return default
        return float(str(val).strip().replace(',', '.'))
    except (ValueError, AttributeError):
        return default

def deg_to_dms(deg_val: float) -> str:
    """Convierte grados decimales a formato sexagesimal (G° M' S.S")."""
    sign = "-" if deg_val < 0 else ""
    val = abs(deg_val)
    d = int(val)
    m_float = (val - d) * 60.0
    m = int(m_float)
    s = (m_float - m) * 60.0
    return f"{sign}{d}° {m:02d}' {s:04.1f}\""

def sec_to_dms(sec_val: float) -> str:
    """Convierte segundos de arco a formato sexagesimal."""
    deg_val = sec_val / 3600.0
    return deg_to_dms(deg_val)

def main(page: ft.Page):
    page.title = "polyGROSS"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 12
    
    rows_data = []
    canvas_size = 310
    plot_canvas = cv.Canvas(width=canvas_size, height=canvas_size, shapes=[])
    
    # 1. Tabla de ingreso de datos
    data_table = ft.DataTable(
        column_spacing=10,
        horizontal_margin=6,
        columns=[
            ft.DataColumn(ft.Text("Vér.", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Lado (m)", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Ángulo (°)", weight=ft.FontWeight.BOLD)),
        ],
        rows=[]
    )

    # Campos opcionales de proyecto y equipo con diseño responsive
    tf_az_init = ft.TextField(value="90.0", label="Azimut V1V2 (°)", dense=True, keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    tf_prec_ang = ft.TextField(value="10", label="Prec. Dirección (\")", dense=True, keyboard_type=ft.KeyboardType.NUMBER, expand=True)
    tf_prec_lin = ft.TextField(value="1.0", label="Prec. Lineal (cm)", dense=True, keyboard_type=ft.KeyboardType.NUMBER, expand=True)

    # 2. Tabla completa de separación de coordenadas
    diff_table = ft.DataTable(
        column_spacing=10,
        horizontal_margin=6,
        columns=[
            ft.DataColumn(ft.Text("Vér.", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Separación (m)", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Adelante (X, Y)", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Atrás (X, Y)", weight=ft.FontWeight.BOLD)),
        ],
        rows=[]
    )

    # Componentes de Cierre Topográfico y Tolerancias
    txt_cierre_lineal = ft.Text("-", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_200)
    txt_cierre_x = ft.Text("-", size=12)
    txt_cierre_y = ft.Text("-", size=12)
    txt_tol_lineal = ft.Text("-", size=12)
    txt_cierre_angular = ft.Text("-", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.CYAN_200)
    txt_tol_angular = ft.Text("-", size=12)

    def update_table():
        data_table.rows.clear()
        for i, row in enumerate(rows_data):
            data_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f"V{i+1}")),
                    ft.DataCell(row["dist"]),
                    ft.DataCell(row["ang"]),
                ])
            )
        page.update()

    def add_row(dist_val="10.0", ang_val="90.0"):
        tf_dist = ft.TextField(
            value=dist_val, 
            width=85, 
            dense=True,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        tf_ang = ft.TextField(
            value=ang_val, 
            width=85, 
            dense=True,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        rows_data.append({"dist": tf_dist, "ang": tf_ang})
        update_table()

    def remove_last_row(e):
        if len(rows_data) > 3:
            rows_data.pop()
            update_table()
        else:
            page.show_snack_bar(
                ft.SnackBar(ft.Text("Se requieren al menos 3 vértices"), open=True)
            )

    # Datos iniciales
    datos_iniciales = [
        ("10.064", "123"),
        ("9.77", "124"),
        ("10.13", "101"),
        ("8.06", "129"),
        ("9.02", "129"),
        ("8.39", "114")
    ]
    for d, a in datos_iniciales:
        add_row(dist_val=d, ang_val=a)

    def draw_polygons(blue, red):
        plot_canvas.shapes.clear()
        
        all_x = [c[0] for c in blue + red]
        all_y = [c[1] for c in blue + red]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        rango_x = max_x - min_x if max_x != min_x else 1.0
        rango_y = max_y - min_y if max_y != min_y else 1.0
        
        margin = 35
        drawable_w = canvas_size - 2 * margin
        drawable_h = canvas_size - 2 * margin
        escala = min(drawable_w / rango_x, drawable_h / rango_y)
        
        def transform(x, y):
            px = margin + (x - min_x) * escala
            py = (canvas_size - margin) - (y - min_y) * escala
            return px, py

        # Camino Azul
        path_blue = cv.Path(
            elements=[cv.Path.MoveTo(*transform(blue[0][0], blue[0][1]))],
            paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.Colors.BLUE_400, stroke_width=2.5)
        )
        for x, y, v in blue[1:]:
            px, py = transform(x, y)
            path_blue.elements.append(cv.Path.LineTo(px, py))
        plot_canvas.shapes.append(path_blue)
        
        for x, y, v in blue:
            px, py = transform(x, y)
            color = ft.Colors.GREEN_ACCENT if v == 1 else ft.Colors.BLUE_300
            plot_canvas.shapes.append(cv.Circle(px, py, 4.5, ft.Paint(color=color)))
            plot_canvas.shapes.append(
                cv.Text(px - 22, py + 6, value=f"V{v}", style=ft.TextStyle(color=color, size=12, weight=ft.FontWeight.BOLD))
            )

        # Camino Rojo
        path_red = cv.Path(
            elements=[cv.Path.MoveTo(*transform(red[0][0], red[0][1]))],
            paint=ft.Paint(style=ft.PaintingStyle.STROKE, color=ft.Colors.RED_400, stroke_width=2)
        )
        for x, y, v in red[1:]:
            px, py = transform(x, y)
            path_red.elements.append(cv.Path.LineTo(px, py))
        plot_canvas.shapes.append(path_red)
        
        for x, y, v in red:
            px, py = transform(x, y)
            if v != 1:
                plot_canvas.shapes.append(cv.Circle(px, py, 4.5, ft.Paint(color=ft.Colors.RED_ACCENT)))
                plot_canvas.shapes.append(
                    cv.Text(px + 6, py - 16, value=f"V{v}", style=ft.TextStyle(color=ft.Colors.RED_ACCENT, size=12, weight=ft.FontWeight.BOLD))
                )

        page.update()

    def calculate_and_plot(e):
        mediciones = []
        for row in rows_data:
            d = parse_num(row["dist"].value, 0.0)
            a = parse_num(row["ang"].value, 0.0)
            mediciones.append((d, a))

        n = len(mediciones)
        if n < 3:
            page.show_snack_bar(ft.SnackBar(ft.Text("Mínimo 3 vértices necesarios"), open=True))
            return

        # Parámetros opcionales
        az_init = parse_num(tf_az_init.value, 90.0) % 360.0
        prec_ang_sec = parse_num(tf_prec_ang.value, 10.0)
        prec_lin_cm = parse_num(tf_prec_lin.value, 1.0)

        # 1. CAMINO AZUL (Adelante)
        coords_blue = [(0.0, 0.0, 1)]
        curr_x, curr_y = 0.0, 0.0
        curr_az = az_init

        sum_dx = 0.0
        sum_dy = 0.0

        for i in range(n):
            d = mediciones[i][0]
            az_rad = math.radians(curr_az)
            dx = d * math.sin(az_rad)
            dy = d * math.cos(az_rad)
            sum_dx += dx
            sum_dy += dy
            
            curr_x += dx
            curr_y += dy
            
            if i < n - 1:
                coords_blue.append((curr_x, curr_y, i + 2))
                ang_interior = mediciones[i + 1][1]
                curr_az = (curr_az + 180.0 - ang_interior) % 360.0

        # Cierre Lineal Topográfico (valores en metros)
        ex = sum_dx
        ey = sum_dy
        el = math.hypot(ex, ey)

        # Cierre Angular
        suma_ang = sum(m[1] for m in mediciones)
        teorico_ang = (n - 2) * 180.0
        err_angular = suma_ang - teorico_ang

        # Tolerancia Angular: T_ang = a * sqrt(2n) en segundos
        tol_ang_sec = prec_ang_sec * math.sqrt(2.0 * n)
        tol_ang_deg = tol_ang_sec / 3600.0
        cumple_ang = abs(err_angular) <= tol_ang_deg

        # Tolerancia Lineal: T_lin = (prec_lin_cm / 100) * sqrt(n) en metros
        tol_lin_m = (prec_lin_cm / 100.0) * math.sqrt(n)
        cumple_lin = el <= tol_lin_m

        # Textos de cierre y tolerancia
        tag_lin = "✅ Cumple" if cumple_lin else "⚠️ Fuera de tol."
        tag_ang = "✅ Cumple" if cumple_ang else "⚠️ Fuera de tol."
        color_lin = ft.Colors.GREEN_ACCENT if cumple_lin else ft.Colors.ORANGE_ACCENT
        color_ang = ft.Colors.GREEN_ACCENT if cumple_ang else ft.Colors.ORANGE_ACCENT

        txt_cierre_lineal.value = f"{el:.4f} m"
        txt_tol_lineal.value = f"Tol. Lineal: ±{tol_lin_m:.4f} m ({tag_lin})"
        txt_tol_lineal.color = color_lin
        txt_cierre_x.value = f"{ex:+.4f} m"
        txt_cierre_y.value = f"{ey:+.4f} m"
        
        txt_cierre_angular.value = f"{deg_to_dms(err_angular)} ({err_angular:+.4f}°)"
        txt_tol_angular.value = f"Tol. Angular [a·√(2n)]: ±{sec_to_dms(tol_ang_sec)} ({tag_ang})"
        txt_tol_angular.color = color_ang

        # 2. CAMINO ROJO (Atrás)
        coords_red = [(0.0, 0.0, 1)]
        curr_x_r, curr_y_r = 0.0, 0.0
        curr_az_r = (az_init + mediciones[0][1]) % 360.0

        for i in range(n - 1):
            idx_side = (n - 1 - i) % n
            d = mediciones[idx_side][0]
            
            az_rad = math.radians(curr_az_r)
            curr_x_r += d * math.sin(az_rad)
            curr_y_r += d * math.cos(az_rad)
            
            coords_red.append((curr_x_r, curr_y_r, idx_side + 1))
            ang_interior = mediciones[idx_side][1]
            curr_az_r = (curr_az_r + ang_interior - 180.0) % 360.0

        draw_polygons(coords_blue, coords_red)

        blue_dict = {v: (x, y) for x, y, v in coords_blue}
        red_dict = {v: (x, y) for x, y, v in coords_red}

        # Calcular separaciones y coordenadas
        diffs = []
        for v in range(1, n + 1):
            if v in blue_dict and v in red_dict:
                bx, by = blue_dict[v]
                rx, ry = red_dict[v]
                dist = math.sqrt((bx - rx) ** 2 + (by - ry) ** 2)
                diffs.append({
                    "v": f"V{v}",
                    "v_num": v,
                    "dist": dist,
                    "bx": bx,
                    "by": by,
                    "rx": rx,
                    "ry": ry
                })

        # Ordenar de menor a mayor separación
        diffs.sort(key=lambda item: item["dist"])

        # Poblar la tabla
        diff_table.rows.clear()
        for d in diffs:
            is_min = d["dist"] < 0.05
            v_color = ft.Colors.GREEN_ACCENT if is_min else None
            diff_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(d["v"], weight=ft.FontWeight.BOLD if is_min else ft.FontWeight.NORMAL, color=v_color)),
                    ft.DataCell(ft.Text(f"{d['dist']:.4f}", weight=ft.FontWeight.BOLD if is_min else ft.FontWeight.NORMAL, color=v_color)),
                    ft.DataCell(ft.Text(f"({d['bx']:.3f}, {d['by']:.3f})")),
                    ft.DataCell(ft.Text(f"({d['rx']:.3f}, {d['ry']:.3f})")),
                ])
            )

        show_tab(1)

    # Botones
    btn_add = ft.ElevatedButton("+ Agregar Vértice", icon=ft.Icons.ADD, on_click=lambda e: add_row())
    btn_del = ft.OutlinedButton("- Borrar Vértice", icon=ft.Icons.REMOVE, on_click=remove_last_row)
    btn_calc = ft.FilledButton("Calcular y Graficar", icon=ft.Icons.AUTO_GRAPH, on_click=calculate_and_plot, height=45)

    # Panel de parámetros opcionales con diseño adaptable y márgenes limpios
    panel_opcionales = ft.Container(
        content=ft.Column([
            ft.Text("Parámetros del Proyecto y Equipo (Opcionales):", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_200),
            ft.Row([tf_az_init], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([tf_prec_ang, tf_prec_lin], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ], spacing=8),
        bgcolor=ft.Colors.BLACK26,
        border_radius=8,
        border=ft.Border.all(1, ft.Colors.WHITE10),
        padding=12,
        margin=ft.Margin(0, 8, 0, 8)
    )

    # Vista desplazable de Datos con márgenes y espaciado correcto
    tab_data_list = ft.ListView([
        ft.Row([btn_add, btn_del], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ft.Divider(height=10),
        ft.Container(
            content=ft.Row([data_table], alignment=ft.MainAxisAlignment.CENTER, scroll=ft.ScrollMode.ADAPTIVE),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.only(bottom=5)
        ),
        ft.Divider(height=10),
        panel_opcionales,
        ft.Container(height=4),
        btn_calc,
        ft.Container(height=60) # Margen inferior amplio para navegación
    ], spacing=10, padding=ft.Padding(4, 8, 4, 50), expand=True)

    tab_data = ft.Container(
        content=tab_data_list,
        padding=0,
        visible=True,
        expand=True
    )

    # 1. Cierre Topográfico con Tolerancias
    card_cierre = ft.Container(
        content=ft.Column([
            ft.Text("Cierre Topográfico y Tolerancias", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300),
            ft.Divider(height=4),
            ft.Row([
                ft.Text("Cierre Lineal:", size=12, weight=ft.FontWeight.W_500),
                txt_cierre_lineal
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([
                ft.Text("eX (m):", size=12),
                txt_cierre_x,
                ft.Text("eY (m):", size=12),
                txt_cierre_y
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            txt_tol_lineal,
            ft.Divider(height=4),
            ft.Row([
                ft.Text("Cierre Angular:", size=12, weight=ft.FontWeight.W_500),
                txt_cierre_angular
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            txt_tol_angular,
        ], spacing=4),
        bgcolor=ft.Colors.BLACK38,
        border_radius=8,
        border=ft.Border.all(1, ft.Colors.CYAN_900),
        padding=10,
        width=340
    )

    # 2. Contenedor de la Tabla de Coordenadas y Separación
    card_tabla = ft.Container(
        content=ft.Column([
            ft.Text("Tabla de Coordenadas y Separación:", size=13, weight=ft.FontWeight.BOLD),
            ft.Row(
                [diff_table],
                scroll=ft.ScrollMode.ADAPTIVE,
                alignment=ft.MainAxisAlignment.CENTER
            )
        ], spacing=6),
        bgcolor=ft.Colors.BLACK26,
        border_radius=8,
        border=ft.Border.all(1, ft.Colors.WHITE10),
        padding=8,
        width=340
    )

    # Vista completa con ListView desplazable
    tab_plot_list = ft.ListView([
        ft.Row([
            ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.BLUE, size=14),
            ft.Text("Adelante", size=12),
            ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.RED, size=14),
            ft.Text("Atrás", size=12),
            ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.GREEN, size=14),
            ft.Text("V1 Inicio", size=12),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(
            content=plot_canvas,
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.BLACK26,
            border_radius=10,
            border=ft.Border.all(1, ft.Colors.WHITE10),
            padding=5,
            width=340
        ),
        ft.Text(
            "El vértice donde coinciden señala el error grosero.", 
            size=13, 
            weight=ft.FontWeight.W_500,
            color=ft.Colors.AMBER_200, 
            text_align=ft.TextAlign.CENTER
        ),
        ft.Divider(height=10),
        # 1. CIERRE TOPOGRÁFICO Y TOLERANCIAS
        card_cierre,
        ft.Divider(height=10),
        # 2. TABLA DE COORDENADAS Y SEPARACIÓN
        card_tabla,
        # Espacio final de scroll
        ft.Container(height=80)
    ], spacing=10, padding=ft.Padding(4, 8, 4, 50), expand=True)

    tab_plot = ft.Container(
        content=tab_plot_list,
        padding=0,
        visible=False,
        expand=True
    )

    def show_tab(idx: int):
        tab_data.visible = (idx == 0)
        tab_plot.visible = (idx == 1)
        nav_bar.selected_index = idx
        page.update()

    def on_nav_change(e):
        show_tab(e.control.selected_index)

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.EDIT_NOTE, label="Datos"),
            ft.NavigationBarDestination(icon=ft.Icons.POLYLINE, label="Gráfico"),
        ],
        selected_index=0,
        on_change=on_nav_change
    )

    page.navigation_bar = nav_bar
    page.add(tab_data, tab_plot)

if __name__ == '__main__':
    ft.run(main)
