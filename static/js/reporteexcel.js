
$(document).ready(function() {
    $('#concepto_nivel_2').select2();
    $('#concepto_nivel_1').select2();
});


        $('#concepto_nivel_1').on('change', function() {
            var conceptoId = $(this).val();
            $.ajax({
                url: '{% url "get_nivel_2_conceptos" %}',
                data: {id_concepto_padre: conceptoId},
                success: function(data) {
                    $('#concepto_nivel_2').empty().append('<option value="todos">Todos los Conceptos Nivel 2</option>');
                    $.each(data, function(index, concepto) {
                        $('#concepto_nivel_2').append('<option value="' + concepto.id + '">' + concepto.concepto_nombre + '</option>');
                    });
                }
            });
        });
$('#formReporte').on('submit', function(event) {
    event.preventDefault();

    const conceptoNivel1 = $('#concepto_nivel_1').val();
    const conceptoNivel2 = $('#concepto_nivel_2').val();
    const fechaInicio = $('#fecha_inicio').val();
    const fechaFinal = $('#fecha_final').val();

        // Validar que ambas fechas estén llenas
    if (!fechaInicio || !fechaFinal) {
        Swal.fire({
            title: 'Error',
            text: 'Por favor, complete ambas fechas: inicio y final.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }
    // Validar que la fecha de inicio no sea posterior a la fecha final
    if (new Date(fechaInicio) > new Date(fechaFinal)) {
        Swal.fire({
            title: 'Error',
            text: 'La fecha de inicio no puede ser posterior a la fecha final.',
            icon: 'warning',
            confirmButtonText: 'Aceptar'
        });
        return;
    }
    $.ajax({
        url: '{% url "generar_reporte_json" %}',
        type: 'GET',
        data: {
            fecha_inicio: fechaInicio,
            fecha_final: fechaFinal,
            concepto_nivel_1: conceptoNivel1,
            concepto_nivel_2: conceptoNivel2,
        },
        success: function(data) {
            generarPDF(data);
        },
        error: function(xhr) {
            // Capturamos y mostramos errores con SweetAlert
            const response = xhr.responseJSON;
            Swal.fire({
                title: 'Error',
                text: response.error || 'Hubo un error al generar el reporte.',
                icon: 'error',
                confirmButtonText: 'Aceptar'
            });
        }
    });
});

function generarPDF(data) {
    const { jsPDF } = window.jspdf;
    if (!jsPDF) {
        alert("jsPDF no está cargado correctamente.");
        return;
    }
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.setFont("helvetica", "bold");
    const conceptoNivel1Texto = $('#concepto_nivel_1 option:selected').text(); // Agregado
    const title = `Reporte - ${conceptoNivel1Texto}`; // Agregado
    const titleWidth = doc.getStringUnitWidth(title) * doc.getFontSize() / doc.internal.scaleFactor;
    const titleX = (doc.internal.pageSize.width - titleWidth) / 2; // Calculamos el X para centrar el título
    doc.text(title, titleX, 20); // Posicionamos el título en la página (X, Y)
    doc.setFontSize(12);
    doc.setFont("helvetica", "normal");
    doc.text(`Fecha: ${data.fecha}`, 20, 30); // Posición Y para la fecha del reporte (20, 30)
    let yPosition = 40;  // La posición de inicio para la tabla y los títulos del grupo
    data.gastos_por_grupo.forEach(group => {
        // Definir las columnas de la tabla
        const columns = ["Proveedor", "Concepto", "Forma de Pago", "Importe", "Fecha"];
        const tableData = [];
        for (let i = 0; i < group.gastos.length; i++) {
            const gasto = group.gastos[i];
            const importe = parseFloat(gasto.importe);
            const importeFormateado = isNaN(importe) ? "0.00" : importe.toFixed(2);
            tableData.push([
                gasto.proveedor,
                gasto.concepto,
                gasto.forma_pago,
                importeFormateado,
                gasto.fecha
            ]);
        }
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text(`Concepto Nivel 2: ${group.nivel_2}`, 20, yPosition);
        yPosition += 10;  // Ajustamos el espacio antes de la tabla
        doc.autoTable(columns, tableData, {
            margin: { top: yPosition }, // La tabla comienza en la posición 'yPosition'
            styles: { fontSize: 10 },
            startY: yPosition, // Comienza en la posición 'yPosition'
        });
        yPosition = doc.lastAutoTable.finalY + 10;  // La posición Y para el siguiente título de grupo
    });
    const totalImporte = parseFloat(data.total_importe);
    const totalImporteFormateado = isNaN(totalImporte) ? "0.00" : totalImporte.toFixed(2);
    const totalText = `Total Importe: ${totalImporteFormateado}`;
    doc.text(totalText, 20, yPosition); // Imprime el total en la posición X=20, Y= después de la última tabla
    doc.save("reporte_gastos.pdf");
}

