# KURDAS OBE - Implementation Roadmap
## Mapping SRS to GitHub Repository

---

## 📋 Project Overview

**Repository**: https://github.com/djambred/kurdas  
**Technology Stack**: Laravel + Filament Admin Panel  
**Purpose**: Outcome-Based Education Curriculum Management System

---

## 🏗️ Phase 1: Core Infrastructure Setup

### 1.1 Environment & Dependencies

```bash
# Install Laravel dependencies
composer require filament/filament:"^3.0"
composer require maatwebsite/excel
composer require barryvdh/laravel-dompdf
composer require spatie/laravel-permission

# Frontend dependencies for visualization
npm install vis-network chart.js
```

### 1.2 Database Architecture

**Create Migrations in order:**

```bash
php artisan make:migration create_universities_table
php artisan make:migration create_faculties_table
php artisan make:migration create_study_programs_table
php artisan make:migration create_graduate_profiles_table
php artisan make:migration create_cpls_table
php artisan make:migration create_courses_table
php artisan make:migration create_cpmks_table
php artisan make:migration create_sub_cpmks_table
php artisan make:migration create_rps_table
php artisan make:migration create_rps_meetings_table
php artisan make:migration create_assessments_table
php artisan make:migration create_course_prerequisites_table
php artisan make:migration create_pl_cpl_mappings_table
php artisan make:migration create_cpl_cpmk_mappings_table
```

---

## 📊 Phase 2: Database Schema Implementation

### 2.1 Core Tables Structure

**universities**
```sql
- id (PK)
- name (string, 255)
- vision (text, nullable)
- mission (text, nullable)
- goals (text, nullable)
- timestamps
```

**faculties**
```sql
- id (PK)
- university_id (FK)
- name (string, 255)
- vision (text, nullable)
- mission (text, nullable)
- goals (text, nullable)
- timestamps
```

**study_programs**
```sql
- id (PK)
- faculty_id (FK)
- name (string, 255)
- code (string, 50, unique)
- type (enum: 'TI', 'SI')
- vision (text, nullable)
- mission (text, nullable)
- goals (text, nullable)
- timestamps
```

**graduate_profiles (PL)**
```sql
- id (PK)
- study_program_id (FK)
- code (string, 50)
- name (string, 255)
- description (text)
- category (string, 100, nullable)
- timestamps
```

**cpls**
```sql
- id (PK)
- study_program_id (FK)
- code (string, 50)
- description (text)
- aspect (enum: 'attitude', 'knowledge', 'skills')
- timestamps
```

**courses**
```sql
- id (PK)
- study_program_id (FK)
- coordinator_id (FK to users)
- code (string, 50, unique)
- name (string, 255)
- type (enum: 'theory', 'practical', 'hybrid', 'online')
- credits (integer)
- semester (integer)
- description (text, nullable)
- timestamps
```

**course_prerequisites**
```sql
- id (PK)
- course_id (FK)
- prerequisite_course_id (FK)
- timestamps
```

**cpmks**
```sql
- id (PK)
- course_id (FK)
- code (string, 50)
- description (text)
- weight (decimal, 5,2)
- timestamps
```

**sub_cpmks**
```sql
- id (PK)
- cpmk_id (FK)
- code (string, 50)
- description (text)
- assessment_indicator (text, nullable)
- timestamps
```

**rps**
```sql
- id (PK)
- course_id (FK)
- study_program_id (FK)
- semester (string, 50)
- academic_year (string, 50)
- status (enum: 'draft', 'review', 'approved', 'rejected')
- approved_by (FK to users, nullable)
- approved_at (timestamp, nullable)
- version (integer, default 1)
- timestamps
```

**rps_meetings**
```sql
- id (PK)
- rps_id (FK)
- meeting_number (integer, 1-14)
- materials (text)
- teaching_materials (text, nullable)
- references (text, nullable)
- methods (json) // ['lecture', 'discussion', 'practical']
- media (json) // ['slides', 'video', 'lab']
- assignments (text, nullable)
- timestamps
```

**assessments**
```sql
- id (PK)
- rps_id (FK)
- component_name (string, 100)
- weight (decimal, 5,2)
- description (text, nullable)
- timestamps
```

**pl_cpl_mappings**
```sql
- id (PK)
- graduate_profile_id (FK)
- cpl_id (FK)
- timestamps
```

**cpl_cpmk_mappings**
```sql
- id (PK)
- cpl_id (FK)
- cpmk_id (FK)
- timestamps
```

---

## 🎯 Phase 3: Filament Resources Implementation

### 3.1 Admin Resources Structure

**File structure:**
```
app/
├── Filament/
│   ├── Resources/
│   │   ├── UniversityResource.php (RF-001.1)
│   │   ├── FacultyResource.php (RF-001.2)
│   │   ├── StudyProgramResource.php (RF-001.3)
│   │   ├── GraduateProfileResource.php (RF-002)
│   │   ├── CplResource.php (RF-003)
│   │   ├── CourseResource.php (RF-004)
│   │   ├── CpmkResource.php (RF-006)
│   │   ├── RpsResource.php (RF-007, RF-008)
│   │   └── AssessmentResource.php (RF-009)
│   ├── Pages/
│   │   ├── PrerequisiteTree.php (RF-005, RF-010)
│   │   ├── Dashboard.php (RF-011)
│   │   ├── PlCplMatrix.php (RF-003.2)
│   │   └── CurriculumVisualization.php (RF-010)
│   └── Widgets/
│       ├── SemesterDistributionChart.php (RF-011.1)
│       └── CourseTypeChart.php (RF-011.2)
```

### 3.2 Key Filament Resources

**UniversityResource.php** (RF-001.1)
```php
<?php
namespace App\Filament\Resources;

use Filament\Resources\Resource;
use Filament\Forms;
use Filament\Tables;

class UniversityResource extends Resource
{
    protected static ?string $model = University::class;
    protected static ?string $navigationIcon = 'heroicon-o-building-library';
    protected static ?string $navigationGroup = 'Institution Management';

    public static function form(Form $form): Form
    {
        return $form->schema([
            Forms\Components\TextInput::make('name')
                ->required()->maxLength(255),
            Forms\Components\Textarea::make('vision')->rows(3),
            Forms\Components\Textarea::make('mission')->rows(3),
            Forms\Components\Textarea::make('goals')->rows(3),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')->searchable(),
                Tables\Columns\TextColumn::make('created_at')->dateTime(),
            ])
            ->filters([])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ]);
    }
}
```

**CourseResource.php** (RF-004)
```php
public static function form(Form $form): Form
{
    return $form->schema([
        Forms\Components\Select::make('study_program_id')
            ->relationship('studyProgram', 'name')->required(),
        Forms\Components\Select::make('coordinator_id')
            ->relationship('coordinator', 'name')->required(),
        Forms\Components\TextInput::make('code')
            ->required()->unique(ignoreRecord: true),
        Forms\Components\TextInput::make('name')->required(),
        Forms\Components\Select::make('type')
            ->options([
                'theory' => 'Theory',
                'practical' => 'Practical',
                'hybrid' => 'Hybrid',
                'online' => 'Online',
            ])->required(),
        Forms\Components\TextInput::make('credits')
            ->numeric()->required()->minValue(1)->maxValue(6),
        Forms\Components\TextInput::make('semester')
            ->numeric()->required()->minValue(1)->maxValue(8),
        Forms\Components\Textarea::make('description')->rows(3),
        
        // Prerequisite Selection (RF-005)
        Forms\Components\Select::make('prerequisites')
            ->multiple()
            ->relationship('prerequisites', 'name')
            ->preload()
            ->helperText('Select courses that must be completed before this course'),
    ]);
}
```

**RpsResource.php** (RF-007, RF-008)
```php
public static function form(Form $form): Form
{
    return $form->schema([
        Forms\Components\Select::make('course_id')
            ->relationship('course', 'name')->required(),
        Forms\Components\TextInput::make('semester')->required(),
        Forms\Components\TextInput::make('academic_year')->required(),
        Forms\Components\Select::make('status')
            ->options([
                'draft' => 'Draft',
                'review' => 'Under Review',
                'approved' => 'Approved',
                'rejected' => 'Rejected',
            ])->default('draft'),
        
        // 14 Meetings Section (RF-007.2)
        Forms\Components\Repeater::make('meetings')
            ->relationship('meetings')
            ->schema([
                Forms\Components\TextInput::make('meeting_number')
                    ->numeric()->required()->minValue(1)->maxValue(14),
                Forms\Components\Textarea::make('materials')
                    ->required()->label('Main Materials'),
                Forms\Components\Textarea::make('teaching_materials')
                    ->label('Teaching Materials'),
                Forms\Components\Textarea::make('references')
                    ->label('References'),
                Forms\Components\CheckboxList::make('methods')
                    ->options([
                        'lecture' => 'Lecture',
                        'discussion' => 'Discussion',
                        'practical' => 'Practical',
                        'simulation' => 'Simulation',
                        'case_study' => 'Case Study',
                    ])->label('Teaching Methods'),
                Forms\Components\CheckboxList::make('media')
                    ->options([
                        'slides' => 'Slides/PPT',
                        'video' => 'Video',
                        'lab' => 'Laboratory',
                        'elearning' => 'E-Learning',
                        'whiteboard' => 'Whiteboard',
                    ])->label('Learning Media'),
                Forms\Components\Textarea::make('assignments')
                    ->label('Assignments/Tasks'),
            ])
            ->defaultItems(14)
            ->collapsible()
            ->itemLabel(fn (array $state): ?string => 
                'Meeting ' . ($state['meeting_number'] ?? '?')),
        
        // Assessment Components (RF-009)
        Forms\Components\Repeater::make('assessments')
            ->relationship('assessments')
            ->schema([
                Forms\Components\TextInput::make('component_name')
                    ->required(),
                Forms\Components\TextInput::make('weight')
                    ->numeric()->required()
                    ->suffix('%')
                    ->minValue(0)->maxValue(100),
                Forms\Components\Textarea::make('description'),
            ])
            ->live()
            ->afterStateUpdated(function ($state, $set) {
                $total = collect($state)->sum('weight');
                if ($total != 100) {
                    // Show warning
                }
            }),
    ]);
}
```

---

## 🌳 Phase 4: Visualization Implementation

### 4.1 Prerequisite Tree (RF-005, RF-010)

**Create Livewire Component:**

```bash
php artisan make:livewire PrerequisiteTreeView
```

**app/Livewire/PrerequisiteTreeView.php**
```php
<?php
namespace App\Livewire;

use Livewire\Component;
use App\Models\Course;
use App\Models\StudyProgram;

class PrerequisiteTreeView extends Component
{
    public $studyProgramId;
    public $courses = [];
    public $edges = [];

    public function mount()
    {
        $this->loadTreeData();
    }

    public function updatedStudyProgramId()
    {
        $this->loadTreeData();
    }

    public function loadTreeData()
    {
        $query = Course::with('prerequisites');
        
        if ($this->studyProgramId) {
            $query->where('study_program_id', $this->studyProgramId);
        }

        $courses = $query->get();

        // Detect cycles (RF-005.2)
        $this->detectCycles($courses);

        // Prepare nodes for Vis.js
        $this->courses = $courses->map(function ($course) {
            return [
                'id' => $course->id,
                'label' => $course->code . '\n' . $course->name,
                'semester' => $course->semester,
                'credits' => $course->credits,
                'level' => $course->semester,
            ];
        })->toArray();

        // Prepare edges
        $this->edges = [];
        foreach ($courses as $course) {
            foreach ($course->prerequisites as $prereq) {
                $this->edges[] = [
                    'from' => $prereq->id,
                    'to' => $course->id,
                    'arrows' => 'to',
                ];
            }
        }
    }

    private function detectCycles($courses)
    {
        // Implement cycle detection algorithm
        // Use DFS to detect cycles in prerequisite graph
        // Set flash message if cycle detected
    }

    public function render()
    {
        return view('livewire.prerequisite-tree-view', [
            'studyPrograms' => StudyProgram::all(),
        ]);
    }
}
```

**resources/views/livewire/prerequisite-tree-view.blade.php**
```html
<div>
    <div class="mb-4">
        <select wire:model.live="studyProgramId" class="form-select">
            <option value="">All Study Programs</option>
            @foreach($studyPrograms as $program)
                <option value="{{ $program->id }}">{{ $program->name }}</option>
            @endforeach
        </select>
    </div>

    <div id="prerequisite-network" style="height: 600px; border: 1px solid #ddd;"></div>

    @push('scripts')
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js"></script>
    <script>
        document.addEventListener('livewire:initialized', () => {
            const container = document.getElementById('prerequisite-network');
            const data = {
                nodes: new vis.DataSet(@json($courses)),
                edges: new vis.DataSet(@json($edges))
            };

            const options = {
                layout: {
                    hierarchical: {
                        direction: 'LR',
                        sortMethod: 'directed',
                        levelSeparation: 200,
                    }
                },
                nodes: {
                    shape: 'box',
                    margin: 10,
                    widthConstraint: { maximum: 200 },
                    font: { size: 12 }
                },
                edges: {
                    smooth: { type: 'cubicBezier' },
                    arrows: { to: { enabled: true, scaleFactor: 0.5 } }
                },
                physics: false
            };

            const network = new vis.Network(container, data, options);

            // Add click event
            network.on('click', function(params) {
                if (params.nodes.length > 0) {
                    const nodeId = params.nodes[0];
                    // Redirect to course details
                    window.location.href = `/admin/courses/${nodeId}/edit`;
                }
            });
        });
    </script>
    @endpush
</div>
```

### 4.2 Dashboard Charts (RF-011)

**Create Filament Widget:**

```bash
php artisan make:filament-widget SemesterDistributionChart --chart
```

**app/Filament/Widgets/SemesterDistributionChart.php**
```php
<?php
namespace App\Filament\Widgets;

use Filament\Widgets\ChartWidget;
use App\Models\Course;

class SemesterDistributionChart extends ChartWidget
{
    protected static ?string $heading = 'Course Distribution by Semester';
    protected static ?int $sort = 2;

    protected function getData(): array
    {
        $distribution = Course::selectRaw('semester, count(*) as count')
            ->groupBy('semester')
            ->orderBy('semester')
            ->pluck('count', 'semester')
            ->toArray();

        return [
            'datasets' => [
                [
                    'label' => 'Number of Courses',
                    'data' => array_values($distribution),
                    'backgroundColor' => '#3b82f6',
                ],
            ],
            'labels' => array_map(fn($s) => "Semester $s", array_keys($distribution)),
        ];
    }

    protected function getType(): string
    {
        return 'bar';
    }
}
```

**app/Filament/Widgets/CourseTypeChart.php**
```php
<?php
namespace App\Filament\Widgets;

use Filament\Widgets\ChartWidget;
use App\Models\Course;

class CourseTypeChart extends ChartWidget
{
    protected static ?string $heading = 'Course Type Distribution';
    protected static ?int $sort = 3;

    protected function getData(): array
    {
        $types = Course::selectRaw('type, count(*) as count')
            ->groupBy('type')
            ->pluck('count', 'type')
            ->toArray();

        return [
            'datasets' => [
                [
                    'data' => array_values($types),
                    'backgroundColor' => ['#f59e0b', '#10b981', '#6366f1', '#ec4899'],
                ],
            ],
            'labels' => array_map('ucfirst', array_keys($types)),
        ];
    }

    protected function getType(): string
    {
        return 'doughnut';
    }
}
```

---

## 📤 Phase 5: Excel Import/Export (RF-012)

### 5.1 Course Export

**app/Exports/CoursesExport.php**
```php
<?php
namespace App\Exports;

use App\Models\Course;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithMapping;

class CoursesExport implements FromCollection, WithHeadings, WithMapping
{
    public function collection()
    {
        return Course::with('studyProgram', 'coordinator')->get();
    }

    public function headings(): array
    {
        return [
            'Code',
            'Name',
            'Study Program',
            'Type',
            'Credits',
            'Semester',
            'Coordinator',
            'Description',
        ];
    }

    public function map($course): array
    {
        return [
            $course->code,
            $course->name,
            $course->studyProgram->name,
            ucfirst($course->type),
            $course->credits,
            $course->semester,
            $course->coordinator->name,
            $course->description,
        ];
    }
}
```

### 5.2 Course Import

**app/Imports/CoursesImport.php**
```php
<?php
namespace App\Imports;

use App\Models\Course;
use App\Models\StudyProgram;
use App\Models\User;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithValidation;

class CoursesImport implements ToModel, WithHeadingRow, WithValidation
{
    public function model(array $row)
    {
        $studyProgram = StudyProgram::where('name', $row['study_program'])->first();
        $coordinator = User::where('email', $row['coordinator_email'])->first();

        return new Course([
            'study_program_id' => $studyProgram->id,
            'coordinator_id' => $coordinator->id,
            'code' => $row['code'],
            'name' => $row['name'],
            'type' => strtolower($row['type']),
            'credits' => $row['credits'],
            'semester' => $row['semester'],
            'description' => $row['description'] ?? null,
        ]);
    }

    public function rules(): array
    {
        return [
            'code' => 'required|unique:courses,code',
            'name' => 'required',
            'study_program' => 'required',
            'type' => 'required|in:theory,practical,hybrid,online',
            'credits' => 'required|integer|min:1|max:6',
            'semester' => 'required|integer|min:1|max:8',
        ];
    }
}
```

### 5.3 Add Export/Import Actions to CourseResource

```php
use Filament\Tables;
use Maatwebsite\Excel\Facades\Excel;
use App\Exports\CoursesExport;
use App\Imports\CoursesImport;

public static function table(Table $table): Table
{
    return $table
        ->columns([...])
        ->headerActions([
            Tables\Actions\Action::make('export')
                ->label('Export to Excel')
                ->icon('heroicon-o-arrow-down-tray')
                ->action(fn () => Excel::download(new CoursesExport, 'courses.xlsx')),
            
            Tables\Actions\Action::make('import')
                ->label('Import from Excel')
                ->icon('heroicon-o-arrow-up-tray')
                ->form([
                    Forms\Components\FileUpload::make('file')
                        ->acceptedFileTypes([
                            'application/vnd.ms-excel',
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        ])
                        ->required(),
                ])
                ->action(function (array $data) {
                    Excel::import(new CoursesImport, $data['file']);
                    Notification::make()
                        ->title('Import successful')
                        ->success()
                        ->send();
                }),
            
            Tables\Actions\Action::make('template')
                ->label('Download Template')
                ->icon('heroicon-o-document-arrow-down')
                ->action(fn () => 
                    Excel::download(new CoursesTemplateExport, 'courses_template.xlsx')),
        ]);
}
```

---

## 📄 Phase 6: RPS PDF Export (RF-013)

**app/Services/RpsPdfGenerator.php**
```php
<?php
namespace App\Services;

use App\Models\Rps;
use Barryvdh\DomPDF\Facade\Pdf;

class RpsPdfGenerator
{
    public function generate(Rps $rps)
    {
        $data = [
            'rps' => $rps->load([
                'course.studyProgram',
                'meetings',
                'assessments',
                'course.cpmks.subCpmks',
            ]),
        ];

        $pdf = Pdf::loadView('pdf.rps', $data)
            ->setPaper('a4', 'portrait')
            ->setOption('margin-top', 10)
            ->setOption('margin-bottom', 10);

        return $pdf->download("RPS_{$rps->course->code}_{$rps->semester}.pdf");
    }
}
```

**resources/views/pdf/rps.blade.php**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>RPS - {{ $rps->course->code }}</title>
    <style>
        body { font-family: Arial, sans-serif; font-size: 10pt; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h2 { margin: 5px 0; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #000; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; font-weight: bold; }
        .section-title { 
            background-color: #4a5568; 
            color: white; 
            padding: 10px; 
            margin: 15px 0 10px 0;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h2>RENCANA PEMBELAJARAN SEMESTER (RPS)</h2>
        <h3>{{ $rps->course->studyProgram->faculty->university->name }}</h3>
        <h3>{{ $rps->course->studyProgram->name }}</h3>
    </div>

    <!-- Course Identity -->
    <table>
        <tr>
            <th width="30%">Course Code</th>
            <td>{{ $rps->course->code }}</td>
        </tr>
        <tr>
            <th>Course Name</th>
            <td>{{ $rps->course->name }}</td>
        </tr>
        <tr>
            <th>Credits</th>
            <td>{{ $rps->course->credits }} SKS</td>
        </tr>
        <tr>
            <th>Semester</th>
            <td>{{ $rps->course->semester }}</td>
        </tr>
        <tr>
            <th>Academic Year</th>
            <td>{{ $rps->academic_year }}</td>
        </tr>
    </table>

    <!-- CPMK Section -->
    <div class="section-title">COURSE LEARNING OUTCOMES (CPMK)</div>
    <table>
        <thead>
            <tr>
                <th width="15%">Code</th>
                <th>Description</th>
                <th width="15%">Weight</th>
            </tr>
        </thead>
        <tbody>
            @foreach($rps->course->cpmks as $cpmk)
            <tr>
                <td>{{ $cpmk->code }}</td>
                <td>{{ $cpmk->description }}</td>
                <td>{{ $cpmk->weight }}%</td>
            </tr>
            @endforeach
        </tbody>
    </table>

    <!-- Assessment Components -->
    <div class="section-title">ASSESSMENT COMPONENTS</div>
    <table>
        <thead>
            <tr>
                <th>Component</th>
                <th width="20%">Weight</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            @foreach($rps->assessments as $assessment)
            <tr>
                <td>{{ $assessment->component_name }}</td>
                <td>{{ $assessment->weight }}%</td>
                <td>{{ $assessment->description }}</td>
            </tr>
            @endforeach
        </tbody>
    </table>

    <!-- 14 Meetings -->
    <div class="section-title">MEETING SCHEDULE (14 Meetings)</div>
    @foreach($rps->meetings as $meeting)
    <table style="page-break-inside: avoid;">
        <tr>
            <th colspan="2" style="background-color: #e2e8f0;">
                Meeting {{ $meeting->meeting_number }}
            </th>
        </tr>
        <tr>
            <th width="30%">Materials</th>
            <td>{{ $meeting->materials }}</td>
        </tr>
        <tr>
            <th>Teaching Materials</th>
            <td>{{ $meeting->teaching_materials }}</td>
        </tr>
        <tr>
            <th>Methods</th>
            <td>{{ implode(', ', $meeting->methods ?? []) }}</td>
        </tr>
        <tr>
            <th>Media</th>
            <td>{{ implode(', ', $meeting->media ?? []) }}</td>
        </tr>
        <tr>
            <th>Assignments</th>
            <td>{{ $meeting->assignments }}</td>
        </tr>
        <tr>
            <th>References</th>
            <td>{{ $meeting->references }}</td>
        </tr>
    </table>
    @endforeach

    <!-- Footer -->
    <div style="margin-top: 30px;">
        <table style="border: none;">
            <tr>
                <td style="border: none; width: 50%;">
                    <p>Prepared by:</p>
                    <p style="margin-top: 50px;">
                        <strong>{{ $rps->course->coordinator->name }}</strong><br>
                        Course Coordinator
                    </p>
                </td>
                <td style="border: none; width: 50%; text-align: right;">
                    @if($rps->status === 'approved')
                    <p>Approved by:</p>
                    <p style="margin-top: 50px;">
                        <strong>{{ $rps->approvedBy->name }}</strong><br>
                        {{ $rps->approved_at->format('d M Y') }}
                    </p>
                    @endif
                </td>
            </tr>
        </table>
    </div>
</body>
</html>
```

**Add PDF export action to RpsResource:**
```php
use App\Services\RpsPdfGenerator;

Tables\Actions\Action::make('exportPdf')
    ->label('Export PDF')
    ->icon('heroicon-o-document-arrow-down')
    ->action(function (Rps $record, RpsPdfGenerator $pdfGenerator) {