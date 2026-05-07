'use client'

import { useEffect, useRef } from 'react'

interface Node {
  id: string
  label: string
  type: 'explored' | 'gap' | 'prerequisite'
  clarity: number
  centrality: number
  bktPL: number
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
  vx?: number
  vy?: number
}

interface Edge {
  source: string | Node
  target: string | Node
  strength: number
}

interface KnowledgeGraphD3Props {
  nodes: Node[]
  edges: Edge[]
  onNodeClick: (nodeId: string) => void
}

export function KnowledgeGraphD3({ nodes, edges, onNodeClick }: KnowledgeGraphD3Props) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || !nodes.length) return

    let mounted = true

    async function buildGraph() {
      const d3 = await import('d3')
      if (!mounted || !svgRef.current) return

      const svg = d3.select(svgRef.current)
      svg.selectAll('*').remove()

      const width = svgRef.current.clientWidth || 600
      const height = svgRef.current.clientHeight || 500

      const nodesCopy = nodes.map(n => ({ ...n }))
      const edgesCopy = edges.map(e => ({ ...e }))

      const simulation = d3.forceSimulation(nodesCopy)
        .force('link', d3.forceLink(edgesCopy).id((d: any) => d.id).distance(120))
        .force('charge', d3.forceManyBody().strength(-250))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collide', d3.forceCollide().radius((d: any) => d.centrality * 28 + 22))

      const link = svg.append('g')
        .selectAll('line')
        .data(edgesCopy)
        .join('line')
        .attr('stroke', '#FFB000')
        .attr('stroke-opacity', 0.25)
        .attr('stroke-width', (d: any) => d.strength * 2)
        .attr('stroke-dasharray', (d: any) => {
          const target = typeof d.target === 'object' ? d.target : nodesCopy.find(n => n.id === d.target)
          return (target as Node)?.type === 'gap' ? '4,4' : 'none'
        })

      const node = svg.append('g')
        .selectAll('circle')
        .data(nodesCopy)
        .join('circle')
        .attr('r', (d: any) => d.centrality * 26 + 10)
        .attr('fill', (d: any) => {
          if (d.type === 'explored') return `rgba(255,176,0,${0.15 + d.bktPL * 0.55})`
          if (d.type === 'gap') return 'rgba(255,255,255,0.07)'
          return 'rgba(255,255,255,0.06)'
        })
        .attr('stroke', (d: any) => d.type === 'explored' ? '#FFB000' : 'rgba(255,255,255,0.45)')
        .attr('stroke-width', 1.5)
        .attr('stroke-dasharray', (d: any) => d.type === 'gap' ? '3,3' : 'none')
        .style('cursor', 'pointer')
        .on('click', (_: any, d: any) => onNodeClick(d.id))

      const label = svg.append('g')
        .selectAll('text')
        .data(nodesCopy)
        .join('text')
        .text((d: any) => d.label)
        .attr('font-family', 'Rubik, sans-serif')
        .attr('font-size', '10px')
        .attr('fill', (d: any) => d.type === 'explored' ? '#EDE0CC' : 'rgba(255,255,255,0.55)')
        .attr('text-anchor', 'middle')
        .attr('pointer-events', 'none')
        .attr('dy', (d: any) => d.centrality * 26 + 22)

      simulation.on('tick', () => {
        link
          .attr('x1', (d: any) => d.source.x)
          .attr('y1', (d: any) => d.source.y)
          .attr('x2', (d: any) => d.target.x)
          .attr('y2', (d: any) => d.target.y)
        node.attr('cx', (d: any) => d.x).attr('cy', (d: any) => d.y)
        label.attr('x', (d: any) => d.x).attr('y', (d: any) => d.y)
      })

      const drag = d3.drag<SVGCircleElement, any>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x; d.fy = d.y
        })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null; d.fy = null
        })

      node.call(drag as any)
    }

    buildGraph()
    return () => { mounted = false }
  }, [nodes, edges, onNodeClick])

  return (
    <svg
      ref={svgRef}
      style={{ width: '100%', height: '100%', background: '#080909' }}
    />
  )
}
