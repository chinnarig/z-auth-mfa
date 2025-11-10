'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Cookies from 'js-cookie'
import toast from 'react-hot-toast'
import { QRCodeSVG } from 'qrcode.react'
import { Shield, LogOut, Key, Download, CheckCircle, XCircle } from 'lucide-react'
import { authAPI, usersAPI } from '@/lib/api'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  company_name: string
  mfa_enabled: boolean
}

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [showMFASetup, setShowMFASetup] = useState(false)
  const [mfaData, setMfaData] = useState<any>(null)
  const [verificationCode, setVerificationCode] = useState('')
  const [backupCodes, setBackupCodes] = useState<string[]>([])
  const [disablePassword, setDisablePassword] = useState('')

  useEffect(() => {
    fetchUser()
  }, [])

  const fetchUser = async () => {
    try {
      const response = await usersAPI.getProfile()
      setUser(response.data)
    } catch (error) {
      toast.error('Failed to load user data')
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    const refreshToken = Cookies.get('refresh_token')
    if (refreshToken) {
      try {
        await authAPI.logout(refreshToken)
      } catch (error) {
        console.error('Logout error:', error)
      }
    }
    
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
    toast.success('Logged out successfully')
    router.push('/login')
  }

  const handleSetupMFA = async () => {
    try {
      const response = await authAPI.setupMFA()
      setMfaData(response.data)
      setShowMFASetup(true)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to setup MFA')
    }
  }

  const handleEnableMFA = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      const response = await authAPI.enableMFA(verificationCode)
      setBackupCodes(response.data.backup_codes)
      toast.success('MFA enabled successfully!')
      await fetchUser()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Invalid verification code')
    }
  }

  const handleDisableMFA = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      await authAPI.disableMFA(disablePassword)
      setDisablePassword('')
      toast.success('MFA disabled successfully')
      await fetchUser()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to disable MFA')
    }
  }

  const downloadBackupCodes = () => {
    const text = backupCodes.join('\n')
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'mfa-backup-codes.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                Voice Agent Platform
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">Welcome back, {user.full_name}!</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User Info Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">Name</dt>
                <dd className="text-sm text-gray-900">{user.full_name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="text-sm text-gray-900">{user.email}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Company</dt>
                <dd className="text-sm text-gray-900">{user.company_name}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Role</dt>
                <dd className="text-sm">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    {user.role.toUpperCase()}
                  </span>
                </dd>
              </div>
            </dl>
          </div>

          {/* MFA Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Multi-Factor Authentication</h2>
              {user.mfa_enabled ? (
                <CheckCircle className="h-6 w-6 text-green-500" />
              ) : (
                <XCircle className="h-6 w-6 text-gray-400" />
              )}
            </div>
            
            <p className="text-sm text-gray-600 mb-4">
              {user.mfa_enabled
                ? 'MFA is enabled on your account. Your account is protected with two-factor authentication.'
                : 'Add an extra layer of security to your account by enabling multi-factor authentication.'}
            </p>

            {!user.mfa_enabled ? (
              !showMFASetup ? (
                <button
                  onClick={handleSetupMFA}
                  className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
                >
                  <Key className="h-4 w-4 mr-2" />
                  Enable MFA
                </button>
              ) : (
                <div className="space-y-4">
                  {!backupCodes.length ? (
                    <>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <p className="text-sm font-medium text-gray-900 mb-2">
                          1. Scan this QR code with your authenticator app
                        </p>
                        <div className="flex justify-center my-4">
                          <QRCodeSVG value={mfaData?.qr_code?.split(',')[1] || ''} size={200} />
                        </div>
                        <p className="text-xs text-gray-600 mb-2">Or enter this code manually:</p>
                        <code className="block text-xs bg-white p-2 rounded border border-gray-200 text-center">
                          {mfaData?.manual_entry_key}
                        </code>
                      </div>

                      <form onSubmit={handleEnableMFA}>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          2. Enter the 6-digit code from your app
                        </label>
                        <input
                          type="text"
                          inputMode="numeric"
                          maxLength={6}
                          value={verificationCode}
                          onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md text-center text-lg tracking-widest"
                          placeholder="000000"
                          required
                        />
                        <button
                          type="submit"
                          disabled={verificationCode.length !== 6}
                          className="mt-4 w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50"
                        >
                          Verify and Enable MFA
                        </button>
                      </form>
                    </>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h3 className="text-sm font-semibold text-yellow-900 mb-2">
                        Save Your Backup Codes
                      </h3>
                      <p className="text-xs text-yellow-800 mb-3">
                        Store these codes in a safe place. You can use them to access your account if you lose your authenticator device.
                      </p>
                      <div className="bg-white p-3 rounded border border-yellow-200 mb-3">
                        {backupCodes.map((code, index) => (
                          <div key={index} className="font-mono text-sm text-gray-900 py-1">
                            {code}
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={downloadBackupCodes}
                        className="w-full flex items-center justify-center px-4 py-2 border border-yellow-300 text-sm font-medium rounded-md text-yellow-900 bg-yellow-100 hover:bg-yellow-200"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download Codes
                      </button>
                    </div>
                  )}
                </div>
              )
            ) : (
              <div className="space-y-4">
                <form onSubmit={handleDisableMFA}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Enter your password to disable MFA
                  </label>
                  <input
                    type="password"
                    value={disablePassword}
                    onChange={(e) => setDisablePassword(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="Enter password"
                    required
                  />
                  <button
                    type="submit"
                    className="mt-4 w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                  >
                    Disable MFA
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
