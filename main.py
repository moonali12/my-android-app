import os
import io

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

Window.clearcolor = (0.95, 0.95, 0.95, 1)

class WeeklyDiaryApp(App):
    def build(self):
        self.title = "Weekly Diary Generator - The Smart School"
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Main Header Title
        header = Label(
            text="The Smart School\nAllama Iqbal Campus Gojra",
            font_size='20sp',
            bold=True,
            color=(0.1, 0.2, 0.4, 1),
            halign='center',
            size_hint_y=None,
            height=60
        )
        main_layout.add_widget(header)

        # Scrollable Form Content
        scroll_view = ScrollView(size_hint=(1, 1))
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Class / Step Input
        form_layout.add_widget(Label(text="Class / Step:", color=(0,0,0,1), size_hint_y=None, height=30, bold=True))
        self.step_input = TextInput(text="Step 1", multiline=False, size_hint_y=None, height=40)
        form_layout.add_widget(self.step_input)

        # Date Range Input
        form_layout.add_widget(Label(text="Date Range:", color=(0,0,0,1), size_hint_y=None, height=30, bold=True))
        self.date_input = TextInput(text="4th to 09th May", multiline=False, size_hint_y=None, height=40)
        form_layout.add_widget(self.date_input)

        self.subjects = ["Al-Quran", "English", "Urdu", "Math", "Rhymes", "Bubbles/G.K"]
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        self.inputs = {}

        # Subjects & Days Input Fields Generation
        for sub in self.subjects:
            form_layout.add_widget(Label(text=f"--- {sub} ---", color=(0.1, 0.3, 0.6, 1), size_hint_y=None, height=35, bold=True))
            self.inputs[sub] = {}
            for day in self.days:
                grid = GridLayout(cols=2, size_hint_y=None, height=40, spacing=5)
                grid.add_widget(Label(text=f"{day}:", color=(0,0,0,1), size_hint_x=0.3))
                
                default_val = "Pg No 31, 32" if sub == "English" and day == "Monday" else ""
                txt_input = TextInput(text=default_val, multiline=False, size_hint_x=0.7)
                self.inputs[sub][day] = txt_input
                grid.add_widget(txt_input)
                form_layout.add_widget(grid)

        scroll_view.add_widget(form_layout)
        main_layout.add_widget(scroll_view)

        # Action Button
        gen_btn = Button(
            text="Generate Printable PDF",
            background_color=(0.1, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=50,
            bold=True
        )
        gen_btn.bind(on_press=self.generate_pdf)
        main_layout.add_widget(gen_btn)

        # Status Display Label
        self.status_label = Label(text="Ready", color=(0, 0.5, 0, 1), size_hint_y=None, height=30)
        main_layout.add_widget(self.status_label)

        return main_layout

    def generate_pdf(self, instance):
        step = self.step_input.text.strip()
        date_range = self.date_input.text.strip()
        
        pdf_filename = f"Weekly_Diary_{step.replace(' ', '_')}.pdf"
        
        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=landscape(A4),
            rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
        )
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], alignment=1, fontSize=20, leading=22, fontName='Helvetica-Bold', textColor=colors.HexColor('#1A365D'))
        subtitle_style = ParagraphStyle('HeaderSub', parent=styles['Normal'], alignment=1, fontSize=12, leading=14, fontName='Helvetica-Bold', textColor=colors.HexColor('#4A5568'))

        elements.append(Paragraph("The Smart School", title_style))
        elements.append(Paragraph("Allama Iqbal Campus Gojra", subtitle_style))
        elements.append(Spacer(1, 10))

        meta_style_left = ParagraphStyle('MetaL', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')
        meta_style_right = ParagraphStyle('MetaR', parent=styles['Normal'], alignment=2, fontSize=11, fontName='Helvetica-Bold')

        meta_table_data = [[
            Paragraph(f"Weekly Diary plan for {step}", meta_style_left),
            Paragraph(f"Date: {date_range}", meta_style_right)
        ]]
        elements.append(Table(meta_table_data, colWidths=[400, 360]))
        elements.append(Spacer(1, 10))

        table_data = [["Day", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]]
        cell_style = ParagraphStyle('CellText', parent=styles['Normal'], alignment=1, fontSize=9, leading=11)

        fri_custom = any(self.inputs[sub]["Friday"].text.strip() for sub in self.subjects)
        sat_custom = any(self.inputs[sub]["Saturday"].text.strip() for sub in self.subjects)

        for idx, sub in enumerate(self.subjects):
            row = [Paragraph(f"<b>{sub}</b>", cell_style)]
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday"]:
                val = self.inputs[sub][day].text.strip()
                row.append(Paragraph(val, cell_style))

            if fri_custom:
                row.append(Paragraph(self.inputs[sub]["Friday"].text.strip(), cell_style))
            elif idx == 0:
                row.append(Paragraph("<b>Activity Day</b><br/><br/>+<br/><br/><b>Reader</b>", cell_style))
            else:
                row.append("")

            if sat_custom:
                row.append(Paragraph(self.inputs[sub]["Saturday"].text.strip(), cell_style))
            elif idx == 0:
                row.append(Paragraph("<b>Books</b><br/><br/>+<br/><br/><b>Reader</b><br/><br/>+<br/><br/><b>Worksheet</b>", cell_style))
            else:
                row.append("")

            table_data.append(row)

        col_widths = [100, 110, 110, 110, 110, 110, 110]
        t = Table(table_data, colWidths=col_widths)
        t_style = [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F7')),
        ]

        if not fri_custom:
            t_style.append(('SPAN', (5, 1), (5, 6)))
            t_style.append(('BACKGROUND', (5, 1), (5, 6), colors.HexColor('#FFFAF0')))
        if not sat_custom:
            t_style.append(('SPAN', (6, 1), (6, 6)))
            t_style.append(('BACKGROUND', (6, 1), (6, 6), colors.HexColor('#FFFAF0')))

        t.setStyle(TableStyle(t_style))
        elements.append(t)
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("<b>Parents Sign: ___________________________</b>", meta_style_left))

        doc.build(elements)
        self.status_label.text = f"Saved: {pdf_filename}"

if __name__ == '__main__':
    WeeklyDiaryApp().run()
