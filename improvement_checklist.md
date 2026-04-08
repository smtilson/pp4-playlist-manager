# PP4 Playlist Manager - Improvement Checklist

## Overview
This document catalogs actionable improvements across the codebase, organized by priority and category. It excludes all-auth boilerplate but captures logic clarity, testing gaps, type safety, and efficiency enhancements.

**Last Updated**: 2026-04-07  
**Test Status**: Basic profiles/queues coverage exists; yt_auth and yt_query nearly untested  
**Type System Status**: Partial (Django ORM attrs untyped); decorators and return contracts recently improved

## Current Activity
We are actively working through item 3, the method-restriction cleanup in [queues/views.py](queues/views.py). `create_queue` is already handled as a GET/POST form view, `edit_queue` is in the expected GET/POST shape, and the remaining focus is the mutation endpoints that should be POST-only or otherwise explicitly constrained. We also added targeted tests for the current behavior, and we are not changing the behavior of the user-written tests. The next view to review is `delete_queue`, followed by `unpublish`, `publish`, `sync`, `add_entry`, `delete_entry`, and `gain_access`.

---

## HIGH PRIORITY - Critical Runtime Risks

### 1. **queues/views.py:create_queue** - Unbound local variable crash
**File**: [queues/views.py](queues/views.py#L25-L37)  
**Issue**: When queue title is empty, `queue` is never created, but line 37 uses `queue.id` in the redirect.  
**Risk**: UnboundLocalError at runtime on empty submissions.  
**Fix**: Return early from empty-title branch; only reference queue after successful creation.  
**Status**: ✅ Completed (implemented in [queues/views.py](queues/views.py#L21-L30)).  
**Test Coverage**: ✅ Added `test_create_queue_POST_empty_title` in [queues/tests.py](queues/tests.py#L172).

### 2. **queues/views.py:swap** - Return contract mismatch  
**File**: [queues/views.py](queues/views.py#L302) calls [queues/models.py](queues/models.py#L278)  
**Issue**: `swap_entry_positions()` has return type `-> None` but returns `(self, other_entry)` on success and `None` implicitly on same-position.  
**Risk**: Unpacking None at line 302 when positions match.  
**Fix**: Make return type consistent: either always return `tuple[Entry, Entry]` or split into two methods.  
**Status**: ✅ Completed (method now consistently returns `tuple[Entry, Entry]`).  
**Implementation**: [queues/models.py](queues/models.py#L278-L288) and [queues/views.py](queues/views.py#L284).  
**Test Coverage**: ✅ Added `test_swap_same_position_returns_unchanged_entries` in [queues/tests.py](queues/tests.py#L619).

### 3. **queues/views.py** - Missing method restrictions on mutations
**File**: Multiple endpoints: [line 105](queues/views.py#L105), [131](queues/views.py#L131), [151](queues/views.py#L151), [178](queues/views.py#L178), [206](queues/views.py#L206), [268](queues/views.py#L268), [322](queues/views.py#L322)  
**Issue**: State-changing operations (delete_queue, unpublish, publish, sync, add_entry, delete_entry, gain_access) accept all HTTP methods including GET.  
**Risk**: CSRF vulnerability; no idempotency guarantee; state changes via GET requests if bypassed.  
**Fix**: Add `@require_POST` and/or stricter method decorators per endpoint semantics.  
**Test Gap**: No HTTP-method restriction tests (e.g., GET to delete_queue should fail).

### 4. **errors/views.py:error_handler** - Null-safe response handling  
**File**: [errors/views.py](errors/views.py#L4)  
**Issue**: Line 5 calls `process_response(response)` on potentially None response. Line 4 has a guard for None but still passes to line 5.  
**Risk**: Crash if response is None in certain error paths.  
**Fix**: Guard process_response call or add defensive .get() on all response attributes.  
**Test Gap**: No test for None response path.

### 5. **utils.py:trigger** - Broken debug function  
**File**: [utils.py](utils.py#L34)  
**Issue**: Uses `object.getattr()` which is not how getattr works (should be `getattr(object, ...)`).  
**Risk**: AttributeError when debug trigger is called.  
**Fix**: Use correct `getattr(object, 'name', '')` syntax, or remove if unused.  
**Note**: Function appears unused; consider removal.

---

## MEDIUM PRIORITY - Logic & Structure Issues

### 6. **queues/views.py:sync** - Duplicate message emission  
**File**: [queues/views.py](queues/views.py#L190-L200)  
**Issue**: Line 194 adds a message inside the NOT queue.synced branch, then line 200 adds another.  
**Risk**: User sees two messages for single action.  
**Fix**: Only add message once per code path; consolidate before line 200.  
**Test Gap**: No assertion checking message uniqueness per action.

### 7. **queues/views.py:gain_access** - Unsafe user type narrowing  
**File**: [queues/views.py](queues/views.py#L333-L365)  
**Issue**: `user = make_user(request)` returns `Union[Profile, GuestProfile]`, but code uses Profile-only attrs at [360](queues/views.py#L360), [361](queues/views.py#L361) without narrowing.  
**Risk**: AttributeError if code path runs with GuestProfile (though guards prevent it currently).  
**Fix**: Add explicit `isinstance(user, Profile)` guard or narrow type in conditional blocks.  
**Type Safety**: Will improve once type narrowing is added.

### 8. **queues/views.py** - Non-standard reverse import  
**File**: [queues/views.py](queues/views.py#L1)  
**Issue**: Imports `reverse` from `django.shortcuts` instead of standard `django.urls`.  
**Risk**: Works at runtime but confuses static analysis tooling.  
**Fix**: Change to `from django.urls import reverse`.  
**Impact**: Will reduce linter noise across the file.

### 8a. **queues/views.py:create_queue** - Split GET and POST handlers  
**File**: [queues/views.py](queues/views.py#L13-L30)  
**Issue**: `create_queue` currently handles both form rendering (GET) and submission (POST) in one method.  
**Risk**: Mixed responsibilities make method restrictions and testing harder to reason about.  
**Fix**: Split into two views: `create_queue_form` (GET) and `create_queue_submit` (POST with `@require_http_methods(["POST"])`).  
**Test Gap**: Add separate tests for GET form render and POST submission flow after split.

### 9. **profiles/views.py** - OAuth callback query params not preserved  
**File**: [profiles/views.py](profiles/views.py#L36)  
**Issue**: OAuth flow detects auth params in path but redirects without preserving them.  
**Risk**: State/code params lost, callback may fail.  
**Fix**: Preserve query string in redirect or call return_from_authorization directly.  
**Note**: TODO comment already present; requires investigation of callback routing.

### 10. **queues/models.py:unpublish & sync** - Return type annotation mismatch  
**File**: [queues/models.py](queues/models.py#L128) declared `-> None` but returns tuple  
**Issue**: Type annotation says returns None but code returns `(msg, msg_type)`.  
**Fix**: Change to `-> tuple[str, int]` matching actual behavior.  
**Impact**: Type checkers will now validate correct unpacking in views.

### 11. **profiles/models.py:Profile** - Related manager type hints insufficient  
**File**: [profiles/models.py](profiles/models.py#L61-L63)  
**Issue**: `my_queues` and `other_queues` are now typed as `Manager[Queue]` in TYPE_CHECKING block, but `.add()` method not available on ManyToMany manager.  
**Fix**: Use more specific `RelatedManager` or handle the ManyToMany-specific `.add()` call separately.  
**Note**: Was previously untyped; recent improvement helps but needs refinement.

---

## TYPE HINTS & DOCSTRINGS - Files Still Needing Cleanup

### Files needing stronger type hints
- [profiles/models.py](profiles/models.py) - `Profile`, `GuestProfile`, and manager attributes still need fuller typing coverage.
- [queues/models.py](queues/models.py) - `Queue` and `Entry` methods still have return-type mismatches and informal annotations.
- [queues/views.py](queues/views.py) - View signatures and helper branches still rely on a mix of implicit and explicit typing.
- [utils.py](utils.py) - Decorators and helper functions still need clearer annotations for request/response flow.
- [yt_query/yt_api_utils.py](yt_query/yt_api_utils.py) - API helper methods need consistent return types for search/session helpers.
- [yt_auth/token_auth.py](yt_auth/token_auth.py) - OAuth helper functions need clearer annotations for path, tokens, and return values.
- [errors/views.py](errors/views.py) - Error handler flow would benefit from explicit response typing.
- [errors/utils.py](errors/utils.py) - Response parsing helpers need clearer typed inputs/outputs.
- [queues/forms.py](queues/forms.py) - Form fields and cleaned-data expectations should be typed where possible.

### Files needing stronger docstrings
- [queues/views.py](queues/views.py) - Several views still have mixed or incomplete docstrings, especially around method behavior and authorization rules.
- [queues/models.py](queues/models.py) - Complex queue and entry methods need clearer behavioral docstrings.
- [profiles/models.py](profiles/models.py) - `GuestProfile` methods and the guest/auth boundary should be documented more clearly.
- [utils.py](utils.py) - Helper functions like decorators, parsing, and debug utilities need explicit intent-focused docstrings.
- [yt_query/yt_api_utils.py](yt_query/yt_api_utils.py) - External API wrappers need docstrings that spell out inputs, outputs, and error behavior.
- [yt_auth/token_auth.py](yt_auth/token_auth.py) - OAuth flow functions need docstrings explaining state, redirect handling, and token exchange behavior.
- [errors/views.py](errors/views.py) - Error routing helpers should document how response status determines the redirect path.
- [errors/utils.py](errors/utils.py) - Internal response-processing helpers need docstrings that explain status handling.


---

## MEDIUM PRIORITY - Missing Tests (Critical Gaps)

### Test Suite 1: **yt_auth/tests.py** - Severely under-tested
**Current State**: 4 lines (essentially empty)  
**External API Integration**: OAuth flow with Google; token exchange; credential storage  
**Critical Test Cases Missing**:
- [ ] OAuth authorization URL generation  
- [ ] Token exchange with invalid state (CSRF simulation)
- [ ] Token refresh on expiry
- [ ] Credentials storage & retrieval  
- [ ] Error handling for network failures (HTTPError)
- [ ] Local vs. production redirect URI handling  

### Test Suite 2: **yt_query/tests.py** - Severely under-tested  
**Current State**: 4 lines (essentially empty)  
**External API Integration**: YouTube Data API search, playlist creation, item management  
**Critical Test Cases Missing**:
- [ ] Search videos by query (mocked API)
- [ ] Find user YouTube channel & handle  
- [ ] Create playlist  
- [ ] Add/remove playlist items  
- [ ] Handle rate-limiting (API quota exceeded)
- [ ] Handle invalid video IDs  
- [ ] Handle private video filtering  

### Test Suite 3: **queues/views.py** - Missing method restriction tests  
**Current State**: 671 lines of tests  
**Coverage Gaps**:
- [ ] GET request to delete_queue (should fail)
- [ ] GET request to publish, sync, unpublish, add_entry (should fail)
- [ ] GET request to gain_access (should fail)  
- [ ] Verify CSRF protection on POST mutations

### Test Suite 4: **queues/views.py:create_queue** - Edge case missing  
**Current State**: Tests exist but incomplete  
**Test Case Missing**:
- [ ] Empty queue title submission (triggers unbound variable bug #1)
- [ ] Whitespace-only title handling

### Test Suite 5: **queues/views.py:swap** - Same-position edge case  
**Current State**: Tests exist but incomplete  
**Test Case Missing**:
- [ ] Swap entry with itself (same position)
- [ ] Swap when position equals current position  

### Test Suite 6: **profiles/views.py:guest_sign_in** - Edge cases  
**Current State**: Tests exist  
**Test Cases Missing**:
- [ ] Empty guest name submission  
- [ ] Only-whitespace guest name  
- [ ] Missing queue_id in session (should raise Http404)

### Test Suite 7: **profiles/views.py:set_name** - Boundary  
**Current State**: Tests exist  
**Test Cases Missing**:
- [ ] Whitespace-only name (should be rejected)
- [ ] POST method required (already has @require_POST but test coverage may be gaps)

### Test Suite 8: **profiles/views.py** - OAuth callback  
**Current State**: Tests exist  
**Test Cases Missing**:
- [ ] OAuth callback with missing state param (error path)
- [ ] OAuth callback with missing code param  
- [ ] State/code param preservation across redirects

### Test Suite 9: **queues/views.py:gain_access** - Authorization & state  
**Current State**: Tests exist  
**Test Cases Missing**:
- [ ] Invalid owner_secret (should reject)
- [ ] Guest user gaining access to queue (set queue_id in session)
- [ ] Authenticated user adding queue to collaborations
- [ ] Duplicate access (adding already-accessible queue)

### Test Suite 10: **errors/views.py:error_handler** - Null safety  
**Current State**: Tests in errors/tests.py  
**Test Cases Missing**:
- [ ] None response handling  
- [ ] 4xx status codes (404, 400, 403)
- [ ] 5xx status codes (500)

---

## LOW PRIORITY - Code Quality & Polish

### 12. **utils.py** - Mixed decorator patterns  
**File**: [utils.py](utils.py#L82+)  
**Issue**: Contains both `require_auth` and `with_error_handling` decorators but profiles/views.py also re-defines some of these.  
**Fix**: Consolidate decorators to one location (either utils or module-specific); clarify import paths.  
**Note**: Recent refactor added these to utils; ensure no duplication exists.

### 13. **queues/views.py** - Error handler boilerplate  
**File**: Every function ends with error_handler wrapping (e.g., lines 40, 101, 127).  
**Issue**: Repetitive and easy to miss.  
**Fix**: Use decorator approach (e.g., @with_error_handling) consistently.  
**Note**: profiles/views.py already uses this pattern; unify across codebase.

### 14. **queues/models.py** - Model docstrings incomplete  
**File**: Queue and Entry classes  
**Issue**: Some methods lack docstrings; complex operations (resort, publish, sync) need clarity.  
**Fix**: Add comprehensive docstrings to all public methods.

### 15. **yt_auth/token_auth.py** - OAuth state validation missing  
**File**: [yt_auth/token_auth.py](yt_auth/token_auth.py#L47+)  
**Issue**: Does not validate state param for CSRF protection.  
**Fix**: Store state in session during auth flow; validate on callback.  
**Note**: OAuth 2.0 best practice; currently not enforced.

### 16. **profiles/models.py** - GuestProfile incomplete  
**File**: [profiles/models.py](profiles/models.py) GuestProfile class  
**Issue**: `convert_to_profile()` method is stubbed (empty).  
**Fix**: Implement actual conversion logic or remove if unused.  
**Note**: Guest-to-authenticated upgrade feature incomplete.

### 17. **utils.py:json_to_dict** - Unsafe JSON parsing  
**File**: [utils.py](utils.py#L14)  
**Issue**: Uses `ast.literal_eval()` instead of `json.loads()` for JSON conversion.  
**Risk**: Unsafe if input is untrusted; ast.literal_eval() can execute code.  
**Fix**: Use `json.loads()` for JSON parsing; clarify intent if literal_eval is needed.

### 18. **pp4_youtube_dj/urls.py** - URL routing clarity  
**File**: [pp4_youtube_dj/urls.py](pp4_youtube_dj/urls.py)  
**Issue**: May benefit from comments explaining routing strategy.  
**Fix**: Add URL grouping comments (auth paths, queue paths, admin, etc.).  
**Low Impact**: Polish only.

### 19. **queues/forms.py** - Form validation  
**File**: [queues/forms.py](queues/forms.py)  
**Issue**: Not reviewed; may need validation rules for queue title, descriptions.  
**Fix**: Review and ensure consistent validation with views.  
**Note**: Currently may rely on view-level validation.

### 20. **Type System** - Complete Profile type hints  
**File**: [profiles/models.py](profiles/models.py) Profile class  
**Issue**: Class comment asks "Should I add type hints here?" - answer is yes.  
**Fix**: Add type hints to Profile methods; use Optional[] for nullable fields.  
**Impact**: Improves IDE support and type checker coverage.

---

## ARCHITECTURAL / DESIGN

### 21. **Guest vs. Authenticated User Pattern**  
**Scope**: profiles/models.py, profiles/views.py, queues/views.py  
**Current Pattern**: `Union[Profile, GuestProfile]` from `make_user()`  
**Issue**: Type union creates many narrowing branches; code is defensive everywhere.  
**Improvement**: Consider single user abstraction (ABC or protocol) with common interface.  
**Impact**: Reduces conditional branches; improves type safety.

### 22. **Message Handling Consistency**  
**Scope**: All view files  
**Current Pattern**: Mix of `messages.add_message()` and `messages.error/success/info()`  
**Status**: Recently standardized in profiles/views.py; needs rollout to queues/views.py  
**Fix**: Ensure all views use high-level functions (messages.success, etc.); remove add_message usage.  
**Test**: Assertion that all message-adding code uses consistent API.

### 23. **Session State Management**  
**Scope**: profiles/views.py (redirect_action, guest_sign_in), queues/views.py (gain_access)  
**Issue**: Session keys used as magic strings (e.g., "redirect_action", "queue_id").  
**Improvement**: Define constants for session keys; centralize session handling.  
**Impact**: Reduces typos; improves maintainability.

### 24. **Error Handling Strategy**  
**Scope**: Throughout codebase  
**Issue**: External API calls (YT API, OAuth) have inconsistent error handling.  
**Pattern Needed**: Consistent try/except for HTTP/ValueError; message to user; logging.  
**Impact**: Better user experience; easier debugging of API issues.

---

## DOCUMENTATION & MIGRATION

### 25. **README.md** - Setup instructions  
**Status**: Unknown current state  
**Missing Documentation**:
- [ ] Local vs. production environment setup  
- [ ] OAuth credentials setup  
- [ ] YouTube API key configuration  
- [ ] Running tests  
- [ ] Deployment instructions  

### 26. **Architectural Decision Log**  
**Status**: None exists  
**Needed**:
- [ ] Why Union[Profile, GuestProfile] instead of ABC
- [ ] Why session-based redirect_action instead of URL params
- [ ] Why cache structure for YouTube data

### 27. **Inline Code Comments**  
**Status**: Some unclear logic has comments; some doesn't  
**Examples Needing Clarification**:
- [ ] `# I don't understand this or statement.` in guest_sign_in (line 224)  
- [ ] OAuth state param handling logic  
- [ ] Queue syncing algorithm

---

## TESTING EXECUTION PLAN (By Priority)

### Phase 1: Critical Bug Coverage (Week 1)
1. Create test_unbound_variable_in_create_queue  
2. Create test_swap_same_position  
3. Create test_http_method_restrictions (all mutation endpoints)  
4. Fix bugs found in phases 1

### Phase 2: External API Coverage (Week 2-3)
1. OAuth token exchange test suite (mocked)
2. YouTube API integration tests (mocked)
3. Error handling for rate limits
4. CSRF state validation

### Phase 3: Edge Cases & Consistency (Week 3-4)
1. Empty/whitespace input validation tests  
2. User type narrowing tests  
3. Message deduplication tests  
4. Session state management tests

### Phase 4: Refactoring & Polish (Ongoing)
1. Apply method decorators to queues/views.py  
2. Consolidate error_handler usage  
3. Type hint improvements  
4. Documentation updates

---

## File Review Status

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| profiles/views.py | ✅ Recently refactored | Maintenance | Decorators, type safety improvements complete |
| queues/views.py | ⚠️ Multiple issues | HIGH | See items #1-3, #6-9 |
| profiles/models.py | ⚠️ Partial | MEDIUM | Type hints added for managers; GuestProfile incomplete |
| queues/models.py | ⚠️ Type annotations | MEDIUM | Return type mismatches (#10) |
| utils.py | ⚠️ Mixed patterns | MEDIUM | Decorators location; json parsing (#12, #17) |
| yt_auth/token_auth.py | ⚠️ Untested | HIGH | See Test Suite 1; CSRF state validation missing |
| yt_query/yt_api_utils.py | ⚠️ Untested | HIGH | See Test Suite 2 |
| errors/views.py | ⚠️ Null handling | MEDIUM | See item #4 |
| errors/utils.py | ⏳ Not yet reviewed | LOW | Process_response logic |
| queues/forms.py | ⏳ Not yet reviewed | LOW | Form validation rules |
| pp4_youtube_dj/settings.py | ✅ Functional | Maintenance | Config is standard Django |
| pp4_youtube_dj/urls.py | ⚠️ Documentation | LOW | Needs routing comments |

---

## Summary Statistics

- **Total Issues Identified**: 27  
- **HIGH Priority**: 5 (critical bugs)  
- **MEDIUM Priority**: 14 (logic/structure/tests)  
- **LOW Priority**: 8 (polish/documentation)  
- **Test Gaps**: 10 major suites  
- **Estimated Effort**: 3-4 weeks for complete addressing at 10 hrs/week

---

## Next Steps

1. **Immediate** (this sprint):
   - Fix critical bugs #1-5 (runtime crashes)
   - Add method restriction decorators to queues/views.py
   - Create yt_auth and yt_query test stubs

2. **Short-term** (next sprint):
   - Implement test suites for external APIs (OAuth, YouTube)
   - Add missing edge case tests
   - Type hint refinements

3. **Long-term**:
   - Architectural refactor for user type system
   - Complete documentation
   - Performance optimization if needed

---

**Document Generated**: 2026-04-07  
**Last Reviewed**: Current  
**Assigned to**: Code review queue
