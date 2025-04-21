import * as d3 from 'd3'

/**
 * Inicializa un gráfico D3 para una señal
 * @param {HTMLElement} container - Elemento contenedor
 * @param {Object} signal - Datos de la señal
 * @returns {Object} - Objeto con referencias al gráfico
 */
export function initializeD3Chart(container, signal) {
  // Limpiar contenedor
  d3.select(container).selectAll('*').remove()
  
  // Dimensiones
  const margin = { top: 20, right: 30, bottom: 30, left: 40 }
  const width = container.clientWidth - margin.left - margin.right
  const height = container.clientHeight - margin.top - margin.bottom
  
  // Crear SVG
  const svg = d3.select(container)
    .append('svg')
    .attr('width', container.clientWidth)
    .attr('height', container.clientHeight)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  
  // Definir escalas
  const xScale = d3.scaleLinear()
    .domain([0, signal.data?.length || 100])
    .range([0, width])
  
  const yScale = d3.scaleLinear()
    .domain(signal.yAxisRange || [-1, 1])
    .range([height, 0])
  
  // Crear ejes
  const xAxis = d3.axisBottom(xScale)
  const yAxis = d3.axisLeft(yScale)
  
  // Añadir ejes
  svg.append('g')
    .attr('class', 'x-axis')
    .attr('transform', `translate(0,${height})`)
    .call(xAxis)
  
  svg.append('g')
    .attr('class', 'y-axis')
    .call(yAxis)
  
  // Crear línea
  const line = d3.line()
    .x((d, i) => xScale(i))
    .y(d => yScale(d))
    .curve(d3.curveMonotoneX)
  
  // Añadir línea (path)
  const path = svg.append('path')
    .datum(signal.data || [])
    .attr('class', 'line')
    .attr('fill', 'none')
    .attr('stroke', signal.color || '#2196f3')
    .attr('stroke-width', 2)
    .attr('d', line)
  
  // Añadir grid (opcional, según configuración)
  if (signal.gridEnabled !== false) {
    // Grid horizontal
    svg.append('g')
      .attr('class', 'grid horizontal-grid')
      .selectAll('line')
      .data(yScale.ticks())
      .enter()
      .append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', d => yScale(d))
      .attr('y2', d => yScale(d))
      .attr('stroke', '#e0e0e0')
      .attr('stroke-dasharray', '3,3')
    
    // Grid vertical
    svg.append('g')
      .attr('class', 'grid vertical-grid')
      .selectAll('line')
      .data(xScale.ticks())
      .enter()
      .append('line')
      .attr('x1', d => xScale(d))
      .attr('x2', d => xScale(d))
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', '#e0e0e0')
      .attr('stroke-dasharray', '3,3')
  }
  
  // Retornar objeto con referencias
  return {
    container,
    svg,
    xScale,
    yScale,
    line,
    path,
    width,
    height,
    margin
  }
}

/**
 * Actualiza un gráfico D3 con nuevos datos
 * @param {Object} chart - Objeto con referencias al gráfico
 * @param {Object} signal - Datos actualizados de la señal
 */
export function updateD3Chart(chart, signal) {
  if (!chart || !signal || !signal.data) return
  
  const { svg, xScale, yScale, line, path } = chart
  
  // Actualizar dominio X si es necesario
  xScale.domain([0, signal.data.length])
  
  // Actualizar dominio Y si es necesario (o usar auto-scale)
  if (signal.autoScale) {
    const min = d3.min(signal.data)
    const max = d3.max(signal.data)
    const padding = (max - min) * 0.1 // 10% de padding
    yScale.domain([min - padding, max + padding])
  } else if (signal.yAxisRange) {
    yScale.domain(signal.yAxisRange)
  }
  
  // Actualizar ejes
  svg.select('.x-axis').call(d3.axisBottom(xScale))
  svg.select('.y-axis').call(d3.axisLeft(yScale))
  
  // Actualizar línea con transición
  path.datum(signal.data)
    .transition()
    .duration(100) // Transición rápida para datos en tiempo real
    .attr('d', line)
    .attr('stroke', signal.color || '#2196f3')
}

/**
 * Añade una etiqueta al gráfico
 * @param {Object} chart - Objeto con referencias al gráfico
 * @param {Object} label - Datos de la etiqueta
 * @returns {Object} - Elemento D3 de la etiqueta
 */
export function addLabel(chart, label) {
  const { svg, xScale, yScale } = chart
  
  // Grupo para la etiqueta
  const labelGroup = svg.append('g')
    .attr('class', 'label')
    .attr('data-id', label.id || `label-${Date.now()}`)
    .attr('transform', `translate(${xScale(label.position)},${yScale(label.value)})`)
  
  // Línea vertical
  labelGroup.append('line')
    .attr('x1', 0)
    .attr('x2', 0)
    .attr('y1', -10)
    .attr('y2', 10)
    .attr('stroke', label.color || '#ff6384')
    .attr('stroke-width', 2)
  
  // Icono (círculo, triángulo, etc. según configuración)
  if (label.icon === 'circle') {
    labelGroup.append('circle')
      .attr('cx', 0)
      .attr('cy', -15)
      .attr('r', 5)
      .attr('fill', label.color || '#ff6384')
  } else if (label.icon === 'triangle') {
    labelGroup.append('path')
      .attr('d', 'M0,-10 L5,-20 L-5,-20 Z')
      .attr('fill', label.color || '#ff6384')
  } else if (label.icon === 'square') {
    labelGroup.append('rect')
      .attr('x', -5)
      .attr('y', -25)
      .attr('width', 10)
      .attr('height', 10)
      .attr('fill', label.color || '#ff6384')
  }
  
  // Texto de la etiqueta
  labelGroup.append('text')
    .attr('x', 0)
    .attr('y', -25)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px')
    .text(label.text || '')
  
  return labelGroup
}

/**
 * Añade una medición (entre dos puntos) al gráfico
 * @param {Object} chart - Objeto con referencias al gráfico
 * @param {Object} measurement - Datos de la medición
 * @returns {Object} - Elemento D3 de la medición
 */
export function addMeasurement(chart, measurement) {
  const { svg, xScale, yScale } = chart
  
  // Grupo para la medición
  const measureGroup = svg.append('g')
    .attr('class', 'measurement')
    .attr('data-id', measurement.id || `measurement-${Date.now()}`)
  
  // Punto A
  const xA = xScale(measurement.pointA)
  const yA = yScale(measurement.valueA)
  
  // Punto B
  const xB = xScale(measurement.pointB)
  const yB = yScale(measurement.valueB)
  
  // Línea entre puntos
  measureGroup.append('line')
    .attr('x1', xA)
    .attr('y1', yA)
    .attr('x2', xB)
    .attr('y2', yB)
    .attr('stroke', measurement.color || '#36a2eb')
    .attr('stroke-width', 2)
    .attr('stroke-dasharray', '5,5')
  
  // Puntos A y B
  measureGroup.append('circle')
    .attr('cx', xA)
    .attr('cy', yA)
    .attr('r', 4)
    .attr('fill', '#ff6384')
  
  measureGroup.append('circle')
    .attr('cx', xB)
    .attr('cy', yB)
    .attr('r', 4)
    .attr('fill', '#36a2eb')
  
  // Etiqueta con valor de la medición
  const midX = (xA + xB) / 2
  const midY = (yA + yB) / 2
  
  // Calcular valores
  const timeDistance = Math.abs(measurement.pointB - measurement.pointA)
  const amplitudeDistance = Math.abs(measurement.valueB - measurement.valueA)
  
  // Etiqueta de tiempo
  measureGroup.append('text')
    .attr('x', midX)
    .attr('y', midY - 15)
    .attr('text-anchor', 'middle')
    .attr('font-size', '11px')
    .attr('font-weight', 'bold')
    .text(`Δt: ${timeDistance.toFixed(2)} ${measurement.timeUnit || 'ms'}`)
  
  // Etiqueta de amplitud
  measureGroup.append('text')
    .attr('x', midX)
    .attr('y', midY + 15)
    .attr('text-anchor', 'middle')
    .attr('font-size', '11px')
    .attr('font-weight', 'bold')
    .text(`ΔA: ${amplitudeDistance.toFixed(2)} ${measurement.amplitudeUnit || ''}`)
  
  return measureGroup
}

/**
 * Habilita el dibujo a mano alzada en el gráfico
 * @param {Object} chart - Objeto con referencias al gráfico
 * @param {Function} callback - Función a llamar cuando se completa un dibujo
 * @returns {Function} - Función para deshabilitar el dibujo
 */
export function enableDrawing(chart, callback) {
  const { svg, width, height } = chart
  
  // Variables para el dibujo
  let isDrawing = false
  let points = []
  let path = null
  
  // Función para generar path SVG
  const pathGenerator = d3.line()
    .x(d => d[0])
    .y(d => d[1])
    .curve(d3.curveBasis)
  
  // Área de dibujo (rectángulo transparente)
  const drawArea = svg.append('rect')
    .attr('class', 'draw-area')
    .attr('width', width + chart.margin.left + chart.margin.right)
    .attr('height', height + chart.margin.top + chart.margin.bottom)
    .attr('transform', `translate(${-chart.margin.left},${-chart.margin.top})`)
    .attr('fill', 'transparent')
    .style('pointer-events', 'all')
  
  // Eventos de mouse/touch
  drawArea
    .on('mousedown', startDrawing)
    .on('mousemove', draw)
    .on('mouseup', endDrawing)
    .on('mouseleave', endDrawing)
    .on('touchstart', startDrawing)
    .on('touchmove', draw)
    .on('touchend', endDrawing)
  
  function startDrawing(event) {
    isDrawing = true
    const coords = d3.pointer(event, this)
    points = [coords]
    
    // Crear nuevo path
    path = svg.append('path')
      .attr('class', 'drawing-path')
      .attr('fill', 'none')
      .attr('stroke', '#ff0000')
      .attr('stroke-width', 2)
      .attr('d', pathGenerator(points))
  }
  
  function draw(event) {
    if (!isDrawing) return
    
    // Añadir nuevo punto
    const coords = d3.pointer(event, this)
    points.push(coords)
    
    // Actualizar path
    path.attr('d', pathGenerator(points))
  }
  
  function endDrawing() {
    if (!isDrawing) return
    isDrawing = false
    
    // Llamar callback con los puntos
    if (points.length > 1 && callback) {
      callback({
        points,
        path: path.attr('d')
      })
    }
  }
  
  // Función para deshabilitar el dibujo
  return function disableDrawing() {
    drawArea.on('mousedown', null)
      .on('mousemove', null)
      .on('mouseup', null)
      .on('mouseleave', null)
      .on('touchstart', null)
      .on('touchmove', null)
      .on('touchend', null)
      .remove()
  }
}

/**
 * Elimina una etiqueta o medición del gráfico
 * @param {Object} chart - Objeto con referencias al gráfico
 * @param {string} id - ID del elemento a eliminar
 * @param {string} type - Tipo de elemento ('label' o 'measurement')
 */
export function removeElement(chart, id, type) {
  const { svg } = chart
  svg.select(`.${type}[data-id="${id}"]`).remove()
}

/**
 * Actualiza los cursores en el gráfico
 * @param {Object} chart - Objeto con referencias al gráfico
 * @param {Object} cursors - Configuración de cursores
 */
export function updateCursors(chart, cursors) {
  const { svg, xScale, height } = chart
  
  // Eliminar cursores existentes
  svg.selectAll('.cursor').remove()
  
  if (!cursors.visible) return
  
  // Añadir cursor A
  if (cursors.cursorA && cursors.cursorA.position !== undefined) {
    const xA = xScale(cursors.cursorA.position)
    
    svg.append('line')
      .attr('class', 'cursor cursor-a')
      .attr('x1', xA)
      .attr('x2', xA)
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', cursors.cursorA.color || '#ff6384')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '5,3')
  }
  
  // Añadir cursor B
  if (cursors.cursorB && cursors.cursorB.position !== undefined) {
    const xB = xScale(cursors.cursorB.position)
    
    svg.append('line')
      .attr('class', 'cursor cursor-b')
      .attr('x1', xB)
      .attr('x2', xB)
      .attr('y1', 0)
      .attr('y2', height)
      .attr('stroke', cursors.cursorB.color || '#36a2eb')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '5,3')
  }
}

/**
 * Actualiza la visibilidad de los elementos de una señal
 * @param {Object} chart - Objeto con referencias al gráfico
 * @param {boolean} visible - Si la señal debe ser visible
 */
export function updateVisibility(chart, visible) {
  if (!chart || !chart.svg) return
  
  chart.svg.style('display', visible ? 'block' : 'none')
}
