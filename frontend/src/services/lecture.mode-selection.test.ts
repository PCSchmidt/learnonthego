import lectureService, { LectureRequest } from './lecture';
import apiClient from './api';

jest.mock('./api', () => ({
  __esModule: true,
  default: {
    postForm: jest.fn(),
  },
}));

describe('Create lecture mode selection', () => {
  const request: LectureRequest = {
    topic: 'Test topic for V2 generation',
    duration: 10,
    difficulty: 'intermediate',
    voice: 'Rachel',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (apiClient.postForm as jest.Mock).mockResolvedValue({ success: true, data: { title: 'ok' } });
  });

  it('uses BYOK endpoint with elevenlabs provider when useByok=true', async () => {
    await lectureService.createLecture(request, { useByok: true, dryRun: true });

    expect(apiClient.postForm).toHaveBeenCalledTimes(1);
    const [endpoint, payload] = (apiClient.postForm as jest.Mock).mock.calls[0];

    expect(endpoint).toBe('/api/lectures/generate-document-v2-byok');
    expect(payload.tts_provider).toBe('elevenlabs');
    expect(payload.llm_provider).toBe('openrouter');
    expect(payload.dry_run).toBe('true');
  });

  it('uses environment endpoint with openai provider when useByok=false', async () => {
    await lectureService.createLecture(request, { useByok: false, dryRun: true });

    expect(apiClient.postForm).toHaveBeenCalledTimes(1);
    const [endpoint, payload] = (apiClient.postForm as jest.Mock).mock.calls[0];

    expect(endpoint).toBe('/api/lectures/generate-document-v2');
    expect(payload.tts_provider).toBe('openai');
    expect(payload.llm_provider).toBe('openrouter');
    expect(payload.dry_run).toBe('true');
  });
});
