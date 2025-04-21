import { ref } from 'vue'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

export function usePdfGenerator() {
  const isGenerating = ref(false)
  const error = ref(null)
  
  // Generar PDF con la visualización actual
  const generatePDF = async (containerId = 'visualization-container', filename = null) => {
    isGenerating.value = true
    error.value = null
    
    try {
      const container = document.getElementById(containerId)
      if (!container) {
        throw new Error(`Contenedor con ID "${containerId}" no encontrado`)
      }
      
      // Crear canvas a partir del contenedor
      const canvas = await html2canvas(container, {
        scale: 2, // Mayor escala para mejor calidad
        useCORS: true,
        logging: false,
        allowTaint: true,
        backgroundColor: '#ffffff'
      })
      
      // Calcular dimensiones para PDF
      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF({
        orientation: 'landscape',
        unit: 'mm',
        format: 'a4'
      })
      
      const imgWidth = 280
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      // Añadir imagen al PDF
      pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight)
      
      // Añadir metadatos
      const timestamp = new Date().toISOString()
      pdf.setProperties({
        title: `Bioseñales - ${timestamp}`,
        subject: 'Visualización de bioseñales',
        creator: 'Sistema de Visualización de Bioseñales',
        keywords: 'bioseñales, visualización, análisis'
      })
      
      // Añadir footer con información
      const pageWidth = pdf.internal.pageSize.getWidth()
      pdf.setFontSize(8)
      pdf.setTextColor(100)
      pdf.text(
        `Generado el ${new Date().toLocaleString()} | Sistema de Visualización de Bioseñales`, 
        pageWidth / 2, 
        200, 
        { align: 'center' }
      )
      
      // Generar nombre del archivo si no se proporcionó
      if (!filename) {
        filename = `biosenales-${timestamp.replace(/:/g, '-').replace(/\./g, '-')}.pdf`
      }
      
      // Descargar PDF
      pdf.save(filename)
      
      return true
    } catch (err) {
      console.error('Error generando PDF:', err)
      error.value = err.message
      return false
    } finally {
      isGenerating.value = false
    }
  }
  
  // Generación con opciones personalizadas
  const generateCustomPDF = async (options = {}) => {
  const {
    containerId = 'visualization-container',
    filename: originalFilename = null,
    title = 'Bioseñales',
      includeTimestamp = true,
      includeFooter = true,
      customText = '',
      orientation = 'landscape',
      format = 'a4'
    } = options
    
    isGenerating.value = true
    error.value = null
    
    try {
      const container = document.getElementById(containerId)
      if (!container) {
        throw new Error(`Contenedor con ID "${containerId}" no encontrado`)
      }
      
      // Crear canvas a partir del contenedor
      const canvas = await html2canvas(container, {
        scale: 2,
        useCORS: true,
        logging: false,
        allowTaint: true,
        backgroundColor: '#ffffff'
      })
      
      // Crear documento PDF
      const pdf = new jsPDF({
        orientation,
        unit: 'mm',
        format
      })
      
      // Dimensiones
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      
      const imgWidth = pageWidth - 20
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      // Título si se solicita
      if (title) {
        pdf.setFontSize(16)
        pdf.setTextColor(0)
        pdf.text(title, pageWidth / 2, 10, { align: 'center' })
      }
      
      // Añadir imagen al PDF (ajustar posición si hay título)
      const yPos = title ? 20 : 10
      pdf.addImage(imgData, 'PNG', 10, yPos, imgWidth, imgHeight)
      
      // Añadir texto personalizado si existe
      if (customText) {
        pdf.setFontSize(10)
        pdf.setTextColor(0)
        pdf.text(customText, 10, yPos + imgHeight + 10)
      }
      
      // Añadir footer con información
      if (includeFooter) {
        pdf.setFontSize(8)
        pdf.setTextColor(100)
        
        let footerText = 'Sistema de Visualización de Bioseñales'
        if (includeTimestamp) {
          footerText = `Generado el ${new Date().toLocaleString()} | ${footerText}`
        }
        
        pdf.text(
          footerText, 
          pageWidth / 2, 
          pageHeight - 10, 
          { align: 'center' }
        )
      }
      
      // Generar nombre del archivo si no se proporcionó
      const timestamp = new Date().toISOString()
      let finalFilename = originalFilename
      if (!finalFilename) {
        finalFilename = `biosenales-${timestamp.replace(/:/g, '-').replace(/\./g, '-')}.pdf`
      }
      
      // Descargar PDF
      pdf.save(finalFilename)

      
      return true
    } catch (err) {
      console.error('Error generando PDF personalizado:', err)
      error.value = err.message
      return false
    } finally {
      isGenerating.value = false
    }
  }
  
  return {
    isGenerating,
    error,
    generatePDF,
    generateCustomPDF
  }
}
