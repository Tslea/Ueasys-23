import { useState, useCallback, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  BookOpen,
  Loader2,
  CheckCircle,
  AlertCircle,
  ArrowLeft,
  Brain,
  Trash2
} from 'lucide-react'
import { Card, Button } from '@/components/common'

// API Base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Character {
  id: string
  name: string
  title?: string
  description?: string
}

interface IndexingResult {
  success: boolean
  documents_indexed: number
  total_chunks: number
  message: string
}

export default function CharacterKnowledge() {
  const { characterId } = useParams<{ characterId: string }>()
  const navigate = useNavigate()
  
  const [character, setCharacter] = useState<Character | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isDragging, setIsDragging] = useState(false)
  const [isIndexing, setIsIndexing] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [result, setResult] = useState<IndexingResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Load character info
  useEffect(() => {
    async function loadCharacter() {
      if (!characterId) return
      
      try {
        const response = await fetch(`${API_BASE}/api/v1/characters/${characterId}`)
        if (response.ok) {
          const data = await response.json()
          setCharacter(data)
        } else {
          setError('Personaggio non trovato')
        }
      } catch (e) {
        setError('Errore nel caricamento del personaggio')
      } finally {
        setIsLoading(false)
      }
    }
    
    loadCharacter()
  }, [characterId])

  // File handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      processFiles(files)
    }
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      processFiles(Array.from(files))
    }
  }

  const processFiles = (files: File[]) => {
    const validFiles = files.filter(f => 
      f.type.includes('text') || 
      f.type.includes('pdf') ||
      f.name.endsWith('.txt') ||
      f.name.endsWith('.md') ||
      f.name.endsWith('.yaml') ||
      f.name.endsWith('.yml') ||
      f.name.endsWith('.json')
    )

    if (validFiles.length === 0) {
      setError('Formato file non supportato. Usa TXT, MD, YAML, JSON o PDF.')
      return
    }

    setUploadedFiles(prev => [...prev, ...validFiles])
    setError(null)
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const readFileContent = async (file: File): Promise<string> => {
    // Check if it's a PDF
    if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          const base64 = (reader.result as string).split(',')[1]
          resolve('__PDF_BASE64__' + base64)
        }
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
    }
    
    // Text files
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  const handleIndexDocuments = async () => {
    if (!characterId || uploadedFiles.length === 0) return
    
    setIsIndexing(true)
    setError(null)
    setResult(null)
    
    try {
      // Read file contents
      const contents = await Promise.all(
        uploadedFiles.map(file => readFileContent(file))
      )
      
      const response = await fetch(`${API_BASE}/api/extract-character/index-documents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          character_id: characterId,
          files: uploadedFiles.map((f, i) => ({
            name: f.name,
            content: contents[i],
            type: f.type
          }))
        })
      })
      
      const data = await response.json()
      setResult(data)
      
      if (data.success) {
        setUploadedFiles([]) // Clear files on success
      }
    } catch (e) {
      setError('Errore durante l\'indicizzazione')
    } finally {
      setIsIndexing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-neon-purple" />
      </div>
    )
  }

  if (!character) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <p className="text-gray-400">{error || 'Personaggio non trovato'}</p>
        <Button className="mt-4" onClick={() => navigate('/admin/characters')}>
          Torna alla Lista
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          onClick={() => navigate('/admin/characters')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Indietro
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-neon-purple/20">
          <Brain className="w-8 h-8 text-neon-purple" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">
            Conoscenza di {character.name}
          </h1>
          <p className="text-gray-400">
            Carica documenti che il personaggio potrà "ricordare" durante le conversazioni
          </p>
        </div>
      </div>

      {/* Info Card */}
      <Card className="bg-neon-purple/5 border-neon-purple/20">
        <div className="flex items-start gap-4">
          <BookOpen className="w-6 h-6 text-neon-purple flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-medium text-white mb-2">Come funziona?</h3>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Carica PDF, libri o documenti con informazioni sul personaggio</li>
              <li>• Il sistema indicizza il contenuto in piccoli "chunk"</li>
              <li>• Durante le chat, il personaggio cerca informazioni rilevanti</li>
              <li>• Usa questa conoscenza per rispondere in modo più accurato</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Upload Area */}
      <Card>
        <h3 className="text-lg font-medium text-white mb-4 flex items-center gap-2">
          <Upload className="w-5 h-5" />
          Carica Documenti
        </h3>
        
        <div
          className={`
            border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer
            ${isDragging 
              ? 'border-neon-purple bg-neon-purple/10' 
              : 'border-gray-700 hover:border-gray-600'
            }
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragging ? 'text-neon-purple' : 'text-gray-500'}`} />
          <p className="text-white mb-2">
            Trascina qui i file o clicca per selezionare
          </p>
          <p className="text-gray-400 text-sm">
            Supportati: PDF, TXT, MD, YAML, JSON
          </p>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".txt,.md,.yaml,.yml,.json,.pdf"
            multiple
            onChange={handleFileSelect}
          />
        </div>

        {/* Uploaded Files */}
        {uploadedFiles.length > 0 && (
          <div className="mt-6 space-y-2">
            <h4 className="text-sm font-medium text-gray-300">
              File da indicizzare ({uploadedFiles.length}):
            </h4>
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between px-4 py-2 rounded-lg bg-void-deep"
              >
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-neon-blue" />
                  <span className="text-white">{file.name}</span>
                  <span className="text-gray-500 text-sm">
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-500 hover:text-red-400 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
            
            <Button
              className="w-full mt-4"
              onClick={handleIndexDocuments}
              disabled={isIndexing}
            >
              {isIndexing ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Indicizzazione in corso...
                </>
              ) : (
                <>
                  <Brain className="w-4 h-4 mr-2" />
                  Indicizza {uploadedFiles.length} Documento/i
                </>
              )}
            </Button>
          </div>
        )}

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4 p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center gap-3"
          >
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-300">{error}</span>
          </motion.div>
        )}

        {/* Result */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mt-4 p-4 rounded-lg ${
              result.success 
                ? 'bg-green-900/20 border border-green-500/30' 
                : 'bg-red-900/20 border border-red-500/30'
            }`}
          >
            <div className="flex items-center gap-3 mb-2">
              {result.success ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-400" />
              )}
              <span className={result.success ? 'text-green-300' : 'text-red-300'}>
                {result.message}
              </span>
            </div>
            {result.success && (
              <div className="text-sm text-gray-400 ml-8">
                <p>📄 Documenti: {result.documents_indexed}</p>
                <p>🧩 Chunk creati: {result.total_chunks}</p>
              </div>
            )}
          </motion.div>
        )}
      </Card>
    </div>
  )
}
