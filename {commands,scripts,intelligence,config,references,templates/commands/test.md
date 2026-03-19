# /test — Test Generation

You are generating **tests** for: $ARGUMENTS

---

## Step 1: Detect Test Framework

```bash
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    print('TEST_FRAMEWORK:', p.get('test_framework'))
    print('LANGUAGE:', p.get('language'))
    print('FRAMEWORK:', p.get('framework'))
    print('TEST_CMD:', p.get('build_commands', {}).get('test'))
except: print('No stack profile')
"
```

Also check for test config files:
```bash
ls jest.config* vitest.config* pytest.ini pyproject.toml .rspec spec/ test/ tests/ 2>/dev/null | head -10
```

---

## Step 2: Load the Code

Read the target file completely. Identify:
- All public functions, methods, classes
- All edge cases implied by the code
- All error paths
- All async operations
- All external dependencies (to mock)

---

## Step 3: Read Project Test Patterns

```bash
# Find existing tests to match project's style
find . -name "*.test.ts" -o -name "*.spec.ts" -o -name "*.test.tsx" \
       -o -name "*_test.py" -o -name "test_*.py" -o -name "*_spec.rb" \
  ! -path '*/node_modules/*' 2>/dev/null | head -5 | xargs cat 2>/dev/null | head -100 || true
```

Match the project's existing test style exactly — naming conventions, describe structure, import style, mock patterns.

---

## Step 4: Generate Tests by Framework

### Jest / Vitest (TypeScript/JavaScript)
```typescript
// [filename].test.ts — co-located with source
import { describe, it, expect, vi, beforeEach } from "vitest"; // or jest
import { [TargetFunction] } from "./[filename]";

describe("[TargetFunction]", () => {
  describe("[scenario]", () => {
    it("should [expected behavior] when [condition]", async () => {
      // Arrange
      const input = [test input];
      const mockDep = vi.fn().mockResolvedValue([mock return]);
      
      // Act
      const result = await [TargetFunction](input, mockDep);
      
      // Assert
      expect(result).toEqual([expected]);
    });
    
    it("should throw [ErrorType] when [invalid condition]", async () => {
      await expect([TargetFunction](null)).rejects.toThrow("[error message]");
    });
  });
});
```

### pytest (Python)
```python
# test_[module].py — in tests/ or alongside module
import pytest
from unittest.mock import Mock, AsyncMock, patch
from [module] import [TargetFunction], [ErrorClass]

class Test[TargetFunction]:
    def test_[behavior]_when_[condition](self):
        # Arrange
        input_data = [test input]
        
        # Act
        result = [TargetFunction](input_data)
        
        # Assert
        assert result == [expected]
    
    def test_raises_when_invalid_input(self):
        with pytest.raises([ErrorClass], match="[error message]"):
            [TargetFunction](None)
    
    @pytest.mark.asyncio
    async def test_async_[behavior](self):
        result = await [async_function]()
        assert result is not None

# Fixtures for complex setup
@pytest.fixture
def sample_user(db):
    return User.objects.create(email="test@example.com", name="Test User")
```

### RSpec (Ruby)
```ruby
# spec/[path]_spec.rb
require "rails_helper"

RSpec.describe [ClassName], type: [:service/:model/:request] do
  describe "#[method_name]" do
    context "when [condition]" do
      let(:user) { create(:user) }
      let(:subject) { described_class.new(user) }
      
      it "[expected behavior]" do
        result = subject.[method_name]
        expect(result).to eq([expected])
      end
    end
    
    context "when [invalid condition]" do
      it "raises [ErrorClass]" do
        expect { subject.[method_name](nil) }.to raise_error([ErrorClass])
      end
    end
  end
end
```

### Go testing
```go
// [module]_test.go — same package
package [package_name]

import (
    "context"
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func Test[FunctionName]_[Scenario](t *testing.T) {
    // Arrange
    ctx := context.Background()
    input := [test input]
    
    // Act
    result, err := [FunctionName](ctx, input)
    
    // Assert
    require.NoError(t, err)
    assert.Equal(t, [expected], result)
}

func Test[FunctionName]_ReturnsError_When[Condition](t *testing.T) {
    ctx := context.Background()
    
    _, err := [FunctionName](ctx, nil)
    
    require.Error(t, err)
    assert.ErrorIs(t, err, ErrInvalidInput)
}
```

---

## Step 5: Coverage Requirements

Generate tests for **all** of:

| Category | What to test |
|----------|-------------|
| Happy path | Normal input → expected output |
| Edge cases | null/nil, empty string/array, 0, negative, max values |
| Error paths | Invalid input, missing required fields, DB failures |
| Auth boundaries | Unauthenticated request, wrong user's resource |
| Async | Rejected promises, timeout behavior |
| Side effects | DB calls made, emails sent, events fired |

---

## Step 6: Run the Tests

After generating:
```bash
[test_command_from_stack_profile]
```

If tests fail: debug and fix them immediately. Never output tests that don't pass.

---

## Step 7: Output

1. Complete test file (copy-paste ready)
2. Command to run just these tests
3. Coverage estimate: "These tests cover [N] of [M] code paths (~X%)"

---

> **Token Target:** ≤ 1000 output tokens. Generate tests, not explanations.
> **Zero-failure requirement:** only output tests that pass when run.
> **Co-locate tests** with source unless project uses a separate test directory.
