import { useState, useCallback, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  Sparkles, 
  User, 
  Brain, 
  BookOpen,
  MessageSquare,
  Save,
  X,
  Loader2,
  CheckCircle,
  AlertCircle,
  Plus,
  Trash2
} from 'lucide-react'
import { Card, Button, Input } from '@/components/common'
import { useCharacterStore, CharacterDraft } from '@/stores'
import { cn } from '@/lib/utils'

// API Base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type SectionKey = 'basic' | 'personality' | 'speaking_style' | 'background'

interface ExtractedData {
  success: boolean
  data: Partial<CharacterDraft>
  confidence: number
  suggestions: string[]
}

// Archetype options matching backend ArchetypeType enum
const ARCHETYPE_OPTIONS = [
  { value: 'hero', label: 'Eroe' },
  { value: 'mentor', label: 'Mentore' },
  { value: 'guardian', label: 'Guardiano' },
  { value: 'trickster', label: 'Imbroglione' },
  { value: 'sage', label: 'Saggio' },
  { value: 'ruler', label: 'Sovrano' },
  { value: 'creator', label: 'Creatore' },
  { value: 'innocent', label: 'Innocente' },
  { value: 'explorer', label: 'Esploratore' },
  { value: 'rebel', label: 'Ribelle' },
  { value: 'lover', label: 'Amante' },
  { value: 'jester', label: 'Giullare' },
  { value: 'everyman', label: 'Uomo Comune' },
  { value: 'caregiver', label: 'Custode' },
  { value: 'magician', label: 'Mago' },
  { value: 'outlaw', label: 'Fuorilegge' },
  { value: 'warrior', label: 'Guerriero' },
  { value: 'shadow', label: 'Ombra' }
]

// Alignment options matching backend AlignmentType enum
const ALIGNMENT_OPTIONS = [
  { value: 'lawful_good', label: 'Legale Buono' },
  { value: 'neutral_good', label: 'Neutrale Buono' },
  { value: 'chaotic_good', label: 'Caotico Buono' },
  { value: 'lawful_neutral', label: 'Legale Neutrale' },
  { value: 'true_neutral', label: 'Neutrale Puro' },
  { value: 'chaotic_neutral', label: 'Caotico Neutrale' },
  { value: 'lawful_evil', label: 'Legale Malvagio' },
  { value: 'neutral_evil', label: 'Neutrale Malvagio' },
  { value: 'chaotic_evil', label: 'Caotico Malvagio' }
]

export default function CharacterCreator() {
  const navigate = useNavigate()
  const { id: editId } = useParams<{ id: string }>()
  const isEditMode = !!editId
  
  const { draft, setDraft, updateDraftSection, resetDraft, createCharacter, updateCharacter, fetchCharacter, selectedCharacter, isLoading } = useCharacterStore()
  
  // UI State
  const [activeSection, setActiveSection] = useState<SectionKey>('basic')
  const [isDragging, setIsDragging] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [extractionResult, setExtractionResult] = useState<ExtractedData | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoadingCharacter, setIsLoadingCharacter] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Load character data if editing
  useEffect(() => {
    if (editId) {
      setIsLoadingCharacter(true)
      fetchCharacter(editId).finally(() => setIsLoadingCharacter(false))
    } else {
      resetDraft()
    }
  }, [editId, fetchCharacter, resetDraft])

  // Populate draft when character is loaded
  useEffect(() => {
    if (isEditMode && selectedCharacter) {
      setDraft({
        name: selectedCharacter.name || '',
        title: selectedCharacter.title || '',
        description: selectedCharacter.description || '',
        archetype: selectedCharacter.archetype || 'hero',
        alignment: selectedCharacter.alignment || 'true_neutral',
        avatar_url: selectedCharacter.avatar_url || '',
        personality: selectedCharacter.personality || {
          traits: [],
          values: [],
          fears: [],
          desires: [],
          speaking_style: '',
          quirks: []
        },
        speaking_style: selectedCharacter.speaking_style || {
          tone: '',
          vocabulary: '',
          patterns: [],
          phrases: []
        },
        background: selectedCharacter.background || {
          origin: '',
          history: '',
          key_events: [],
          relationships: {}
        }
      })
    }
  }, [isEditMode, selectedCharacter, setDraft])

  // Drag & Drop handlers
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
      await processFiles(files)
    }
  }, [])

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      await processFiles(Array.from(files))
    }
  }

  const processFiles = async (files: File[]) => {
    // Filter valid files (text, PDF, doc, etc.)
    const validFiles = files.filter(f => 
      f.type.includes('text') || 
      f.type.includes('pdf') ||
      f.type.includes('document') ||
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
    setIsExtracting(true)
    setError(null)

    try {
      // Read file contents
      const contents = await Promise.all(
        validFiles.map(file => readFileContent(file))
      )

      // Send to AI extraction endpoint
      const response = await fetch(`${API_BASE}/api/extract-character`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          files: validFiles.map((f, i) => ({
            name: f.name,
            content: contents[i],
            type: f.type
          }))
        })
      })

      if (!response.ok) {
        // Fallback: simulate extraction locally
        const extracted = simulateExtraction(contents.join('\n\n'))
        setExtractionResult(extracted)
        
        // Auto-populate draft with extracted data
        if (extracted.success) {
          setDraft(extracted.data)
        }
      } else {
        const result: ExtractedData = await response.json()
        setExtractionResult(result)
        
        if (result.success) {
          setDraft(result.data)
        }
      }
    } catch {
      // Fallback simulation
      const contents = await Promise.all(
        validFiles.map(file => readFileContent(file))
      )
      const extracted = simulateExtraction(contents.join('\n\n'))
      setExtractionResult(extracted)
      
      if (extracted.success) {
        setDraft(extracted.data)
      }
    } finally {
      setIsExtracting(false)
    }
  }

  const readFileContent = async (file: File): Promise<string> => {
    // For PDF files, send as base64 - backend will handle extraction
    if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          const base64 = e.target?.result as string
          // Mark it as base64 PDF so backend knows to decode it
          resolve(`__PDF_BASE64__${base64}`)
        }
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
    }
    
    // For text files, use FileReader
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => resolve(e.target?.result as string || '')
      reader.onerror = reject
      reader.readAsText(file)
    })
  }

  // Simulate AI extraction when backend is not available
  const simulateExtraction = (content: string): ExtractedData => {
    const lowerContent = content.toLowerCase()
    
    // Simple pattern matching for demo
    const nameMatch = content.match(/name[:\s]+([^\n]+)/i)
    const descMatch = content.match(/description[:\s]+([^\n]+)/i)
    const traitsMatch = content.match(/traits?[:\s]+([^\n]+)/i)
    
    // Use lowerContent for any case-insensitive checks if needed
    const hasName = lowerContent.includes('name')
    
    return {
      success: true,
      confidence: hasName ? 0.85 : 0.75,
      suggestions: [
        'Rivedi la sezione personalità per maggior dettaglio',
        'Aggiungi relazioni con altri personaggi',
        'Definisci meglio le motivazioni'
      ],
      data: {
        name: nameMatch?.[1]?.trim() || '',
        description: descMatch?.[1]?.trim() || '',
        archetype: 'hero',
        alignment: 'true_neutral',
        personality: {
          traits: traitsMatch?.[1]?.split(',').map((s: string) => s.trim()) || [],
          values: [],
          fears: [],
          desires: [],
          quirks: []
        },
        speaking_style: {
          tone: '',
          vocabulary: '',
          patterns: [],
          phrases: []
        },
        background: {
          origin: '',
          history: '',
          key_events: [],
          relationships: {}
        }
      }
    }
  }

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_: File, i: number) => i !== index))
  }

  const handleSave = async () => {
    if (!draft.name) {
      setError('Il nome del personaggio è obbligatorio')
      return
    }

    try {
      let characterId: string
      
      if (isEditMode && editId) {
        // Update existing character
        await updateCharacter(editId, draft)
        characterId = editId
      } else {
        // Create new character
        const newCharacter = await createCharacter(draft)
        characterId = newCharacter?.id
      }
      
      // If we have uploaded files, index them for this character
      if (uploadedFiles.length > 0 && characterId) {
        try {
          const fileContents = await Promise.all(
            uploadedFiles.map(file => readFileContent(file))
          )
          
          // Use the correct indexing endpoint
          const indexResponse = await fetch(
            `${API_BASE}/api/extract-character/index-documents`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                character_id: characterId,
                files: uploadedFiles.map((f, i) => ({
                  name: f.name,
                  content: fileContents[i],
                  type: f.type
                }))
              })
            }
          )
          
          if (indexResponse.ok) {
            const indexResult = await indexResponse.json()
            console.log(
              `✅ Indicizzati ${indexResult.documents_indexed} documenti ` +
              `(${indexResult.total_chunks} chunks)`
            )
          } else {
            console.warn('Document indexing returned error:', await indexResponse.text())
          }
        } catch (indexError) {
          console.warn('Document indexing failed:', indexError)
          // Don't fail the whole operation, character is already saved
        }
      }
      
      resetDraft()
      navigate('/admin/characters')
    } catch {
      setError('Errore durante il salvataggio')
    }
  }

  const sections: { key: SectionKey; label: string; icon: React.ElementType }[] = [
    { key: 'basic', label: 'Info Base', icon: User },
    { key: 'personality', label: 'Personalità', icon: Brain },
    { key: 'speaking_style', label: 'Stile Parlato', icon: MessageSquare },
    { key: 'background', label: 'Background', icon: BookOpen }
  ]

  // Show loading while fetching character for edit
  if (isLoadingCharacter) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-neon-purple" />
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-fantasy font-bold text-white">
            {isEditMode ? 'Modifica Personaggio' : 'Crea Personaggio'}
          </h1>
          <p className="text-gray-400 mt-1">
            {isEditMode 
              ? `Modifica i dettagli di ${draft.name || 'questo personaggio'}`
              : 'Definisci un nuovo personaggio per il tuo mondo fantasy'
            }
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="ghost"
            onClick={() => {
              resetDraft()
              navigate('/admin/characters')
            }}
          >
            <X className="w-4 h-4 mr-2" />
            Annulla
          </Button>
          <Button
            onClick={handleSave}
            disabled={isLoading || !draft.name}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            {isEditMode ? 'Salva Modifiche' : 'Salva Personaggio'}
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-lg bg-red-900/20 border border-red-500/30 flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-red-400" />
          <span className="text-red-200">{error}</span>
          <button 
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            <X className="w-4 h-4" />
          </button>
        </motion.div>
      )}

      {/* AI Extraction Zone */}
      <Card className="overflow-hidden">
        <div
          className={cn(
            "p-8 border-2 border-dashed rounded-lg transition-all duration-300",
            isDragging 
              ? "border-fantasy-accent bg-fantasy-accent/10" 
              : "border-gray-700 hover:border-gray-600"
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="text-center">
            <div className="mx-auto w-16 h-16 rounded-full bg-gradient-to-br from-fantasy-accent/20 to-fantasy-purple/20 flex items-center justify-center mb-4">
              {isExtracting ? (
                <Loader2 className="w-8 h-8 text-fantasy-accent animate-spin" />
              ) : (
                <Upload className="w-8 h-8 text-fantasy-accent" />
              )}
            </div>
            <h3 className="text-lg font-medium text-white mb-2">
              {isExtracting ? 'Estrazione in corso...' : 'Carica un file per estrarre i dati'}
            </h3>
            <p className="text-gray-400 mb-4">
              Trascina qui un file TXT, MD, YAML, JSON o PDF con la descrizione del personaggio
            </p>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".txt,.md,.yaml,.yml,.json,.pdf"
              multiple
              onChange={handleFileSelect}
            />
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={isExtracting}
            >
              <FileText className="w-4 h-4 mr-2" />
              Seleziona File
            </Button>
          </div>

          {/* Uploaded Files */}
          {uploadedFiles.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-700">
              <h4 className="text-sm font-medium text-gray-300 mb-3">File caricati:</h4>
              <div className="flex flex-wrap gap-2">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 text-sm"
                  >
                    <FileText className="w-4 h-4 text-fantasy-accent" />
                    <span className="text-gray-300">{file.name}</span>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-gray-500 hover:text-red-400"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Extraction Result */}
          {extractionResult && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 pt-6 border-t border-gray-700"
            >
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-green-300 font-medium">
                  Dati estratti con successo
                </span>
                <span className="text-sm text-gray-500">
                  (Confidenza: {Math.round(extractionResult.confidence * 100)}%)
                </span>
              </div>
              
              {extractionResult.suggestions.length > 0 && (
                <div className="p-3 rounded-lg bg-yellow-900/20 border border-yellow-500/30">
                  <h4 className="text-sm font-medium text-yellow-300 mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Suggerimenti AI
                  </h4>
                  <ul className="text-sm text-yellow-200/80 space-y-1">
                    {extractionResult.suggestions.map((s, i) => (
                      <li key={i}>• {s}</li>
                    ))}
                  </ul>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </Card>

      {/* Form Sections */}
      <div className="flex gap-4">
        {sections.map((section) => (
          <button
            key={section.key}
            onClick={() => setActiveSection(section.key)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg transition-all",
              activeSection === section.key
                ? "bg-fantasy-accent text-white"
                : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
            )}
          >
            <section.icon className="w-4 h-4" />
            {section.label}
          </button>
        ))}
      </div>

      {/* Active Section Content */}
      <Card className="min-h-[400px]">
        <AnimatePresence mode="wait">
          {activeSection === 'basic' && (
            <BasicInfoSection 
              draft={draft} 
              setDraft={setDraft} 
            />
          )}
          {activeSection === 'personality' && (
            <PersonalitySection 
              data={draft.personality as PersonalityData} 
              onChange={(data) => updateDraftSection('personality', data)} 
            />
          )}
          {activeSection === 'speaking_style' && (
            <SpeakingStyleSection 
              data={draft.speaking_style as SpeakingStyleData} 
              onChange={(data) => updateDraftSection('speaking_style', data)} 
            />
          )}
          {activeSection === 'background' && (
            <BackgroundSection 
              data={draft.background as BackgroundData} 
              onChange={(data) => updateDraftSection('background', data)} 
            />
          )}
        </AnimatePresence>
      </Card>
    </div>
  )
}

// Type definitions for section data
interface PersonalityData {
  traits?: string[]
  values?: string[]
  fears?: string[]
  desires?: string[]
  quirks?: string[]
}

interface SpeakingStyleData {
  tone?: string
  vocabulary?: string
  patterns?: string[]
  phrases?: string[]
}

interface BackgroundData {
  origin?: string
  history?: string
  key_events?: string[]
  relationships?: Record<string, string>
}

// Section Components
function BasicInfoSection({ draft, setDraft }: { 
  draft: CharacterDraft
  setDraft: (data: Partial<CharacterDraft>) => void 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="space-y-6"
    >
      <h3 className="text-xl font-fantasy text-white mb-4">Informazioni Base</h3>
      
      <div className="grid md:grid-cols-2 gap-6">
        <Input
          label="Nome *"
          placeholder="Es. Gandalf il Grigio"
          value={draft.name}
          onChange={(e) => setDraft({ name: e.target.value })}
        />
        <Input
          label="Titolo"
          placeholder="Es. Il Bianco, Il Saggio..."
          value={draft.title || ''}
          onChange={(e) => setDraft({ title: e.target.value })}
        />
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Archetipo *
          </label>
          <select
            className="w-full px-4 py-2.5 rounded-lg bg-void-deep border border-gray-700 text-white focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all"
            value={draft.archetype}
            onChange={(e) => setDraft({ archetype: e.target.value })}
          >
            {ARCHETYPE_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value} className="bg-gray-900">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Allineamento
          </label>
          <select
            className="w-full px-4 py-2.5 rounded-lg bg-void-deep border border-gray-700 text-white focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all"
            value={draft.alignment}
            onChange={(e) => setDraft({ alignment: e.target.value })}
          >
            {ALIGNMENT_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value} className="bg-gray-900">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
        
        <Input
          label="URL Avatar"
          placeholder="https://..."
          value={draft.avatar_url}
          onChange={(e) => setDraft({ avatar_url: e.target.value })}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Descrizione
        </label>
        <textarea
          className="w-full px-4 py-3 rounded-lg bg-void-deep border border-gray-700 text-white placeholder-gray-500 focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all resize-none"
          rows={4}
          placeholder="Una descrizione dettagliata del personaggio..."
          value={draft.description}
          onChange={(e) => setDraft({ description: e.target.value })}
        />
      </div>
    </motion.div>
  )
}

function PersonalitySection({ data, onChange }: { 
  data: PersonalityData
  onChange: (data: PersonalityData) => void 
}) {
  const addItem = (field: keyof PersonalityData) => {
    const currentValue = data[field]
    if (Array.isArray(currentValue)) {
      onChange({ ...data, [field]: [...currentValue, ''] })
    } else {
      onChange({ ...data, [field]: [''] })
    }
  }

  const updateItem = (field: keyof PersonalityData, index: number, value: string) => {
    const currentValue = data[field]
    if (Array.isArray(currentValue)) {
      const arr = [...currentValue]
      arr[index] = value
      onChange({ ...data, [field]: arr })
    }
  }

  const removeItem = (field: keyof PersonalityData, index: number) => {
    const currentValue = data[field]
    if (Array.isArray(currentValue)) {
      onChange({ ...data, [field]: currentValue.filter((_: string, i: number) => i !== index) })
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="space-y-6"
    >
      <h3 className="text-xl font-fantasy text-white mb-4">Personalità</h3>

      <ArrayField
        label="Tratti Caratteriali"
        items={data.traits || []}
        onAdd={() => addItem('traits')}
        onUpdate={(i: number, v: string) => updateItem('traits', i, v)}
        onRemove={(i: number) => removeItem('traits', i)}
        placeholder="Es. Saggio, Paziente, Misterioso..."
      />

      <ArrayField
        label="Valori"
        items={data.values || []}
        onAdd={() => addItem('values')}
        onUpdate={(i: number, v: string) => updateItem('values', i, v)}
        onRemove={(i: number) => removeItem('values', i)}
        placeholder="Es. Libertà, Conoscenza..."
      />

      <ArrayField
        label="Paure"
        items={data.fears || []}
        onAdd={() => addItem('fears')}
        onUpdate={(i: number, v: string) => updateItem('fears', i, v)}
        onRemove={(i: number) => removeItem('fears', i)}
        placeholder="Es. Perdere il controllo..."
      />

      <ArrayField
        label="Desideri"
        items={data.desires || []}
        onAdd={() => addItem('desires')}
        onUpdate={(i: number, v: string) => updateItem('desires', i, v)}
        onRemove={(i: number) => removeItem('desires', i)}
        placeholder="Es. Proteggere la Terra di Mezzo..."
      />

      <ArrayField
        label="Peculiarità"
        items={data.quirks || []}
        onAdd={() => addItem('quirks')}
        onUpdate={(i: number, v: string) => updateItem('quirks', i, v)}
        onRemove={(i: number) => removeItem('quirks', i)}
        placeholder="Es. Parla in enigmi..."
      />
    </motion.div>
  )
}

function SpeakingStyleSection({ data, onChange }: { 
  data: SpeakingStyleData
  onChange: (data: SpeakingStyleData) => void 
}) {
  const addItem = (field: 'patterns' | 'phrases') => {
    onChange({ ...data, [field]: [...(data[field] || []), ''] })
  }

  const updateItem = (field: 'patterns' | 'phrases', index: number, value: string) => {
    const arr = [...(data[field] || [])]
    arr[index] = value
    onChange({ ...data, [field]: arr })
  }

  const removeItem = (field: 'patterns' | 'phrases', index: number) => {
    onChange({ ...data, [field]: (data[field] || []).filter((_: string, i: number) => i !== index) })
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="space-y-6"
    >
      <h3 className="text-xl font-fantasy text-white mb-4">Stile di Parlato</h3>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Tono
        </label>
        <textarea
          className="w-full px-4 py-3 rounded-lg bg-void-deep border border-gray-700 text-white placeholder-gray-500 focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all resize-none"
          rows={2}
          placeholder="Es. Saggio e pacato, con un tocco di umorismo nascosto..."
          value={data.tone || ''}
          onChange={(e) => onChange({ ...data, tone: e.target.value })}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Vocabolario
        </label>
        <textarea
          className="w-full px-4 py-3 rounded-lg bg-void-deep border border-gray-700 text-white placeholder-gray-500 focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all resize-none"
          rows={2}
          placeholder="Es. Arcaico, ricco di metafore, usa termini della Terra di Mezzo..."
          value={data.vocabulary || ''}
          onChange={(e) => onChange({ ...data, vocabulary: e.target.value })}
        />
      </div>

      <ArrayField
        label="Pattern Linguistici"
        items={data.patterns || []}
        onAdd={() => addItem('patterns')}
        onUpdate={(i: number, v: string) => updateItem('patterns', i, v)}
        onRemove={(i: number) => removeItem('patterns', i)}
        placeholder="Es. Ripete tre volte per enfasi..."
      />

      <ArrayField
        label="Frasi Tipiche"
        items={data.phrases || []}
        onAdd={() => addItem('phrases')}
        onUpdate={(i: number, v: string) => updateItem('phrases', i, v)}
        onRemove={(i: number) => removeItem('phrases', i)}
        placeholder="Es. 'Un mago non arriva mai in ritardo...'"
      />
    </motion.div>
  )
}

function BackgroundSection({ data, onChange }: { 
  data: BackgroundData
  onChange: (data: BackgroundData) => void 
}) {
  const addKeyEvent = () => {
    onChange({ ...data, key_events: [...(data.key_events || []), ''] })
  }

  const updateKeyEvent = (index: number, value: string) => {
    const arr = [...(data.key_events || [])]
    arr[index] = value
    onChange({ ...data, key_events: arr })
  }

  const removeKeyEvent = (index: number) => {
    onChange({ ...data, key_events: (data.key_events || []).filter((_: string, i: number) => i !== index) })
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="space-y-6"
    >
      <h3 className="text-xl font-fantasy text-white mb-4">Background</h3>

      <Input
        label="Origine"
        placeholder="Es. Valinor, le Terre Immortali"
        value={data.origin || ''}
        onChange={(e) => onChange({ ...data, origin: e.target.value })}
      />

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Storia
        </label>
        <textarea
          className="w-full px-4 py-3 rounded-lg bg-void-deep border border-gray-700 text-white placeholder-gray-500 focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all resize-none"
          rows={5}
          placeholder="La storia completa del personaggio..."
          value={data.history || ''}
          onChange={(e) => onChange({ ...data, history: e.target.value })}
        />
      </div>

      <ArrayField
        label="Eventi Chiave"
        items={data.key_events || []}
        onAdd={addKeyEvent}
        onUpdate={(i: number, v: string) => updateKeyEvent(i, v)}
        onRemove={(i: number) => removeKeyEvent(i)}
        placeholder="Es. Battaglia dei Cinque Eserciti..."
      />
    </motion.div>
  )
}

// Reusable Array Field Component
function ArrayField({
  label,
  items,
  onAdd,
  onUpdate,
  onRemove,
  placeholder
}: {
  label: string
  items: string[]
  onAdd: () => void
  onUpdate: (index: number, value: string) => void
  onRemove: (index: number) => void
  placeholder: string
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-300">{label}</label>
        <button
          onClick={onAdd}
          className="flex items-center gap-1 text-sm text-fantasy-accent hover:text-fantasy-gold transition-colors"
        >
          <Plus className="w-4 h-4" />
          Aggiungi
        </button>
      </div>
      <div className="space-y-2">
        {items.map((item: string, index: number) => (
          <div key={index} className="flex gap-2">
            <input
              className="flex-1 px-4 py-2.5 rounded-lg bg-void-deep border border-gray-700 text-white placeholder-gray-500 focus:border-neon-purple focus:ring-1 focus:ring-neon-purple transition-all"
              placeholder={placeholder}
              value={item}
              onChange={(e) => onUpdate(index, e.target.value)}
            />
            <button
              onClick={() => onRemove(index)}
              className="p-2.5 rounded-lg bg-red-900/30 text-red-400 hover:bg-red-900/50 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-sm text-gray-500 italic">
            Nessun elemento. Clicca "Aggiungi" per iniziare.
          </p>
        )}
      </div>
    </div>
  )
}
